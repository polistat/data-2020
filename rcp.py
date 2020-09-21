from datetime import datetime

from bs4 import BeautifulSoup
import xlsxwriter
import requests

workbook = xlsxwriter.Workbook('polls.xlsx')
date = workbook.add_format({'num_format': 'mm/dd/yy'})

races = {'https://www.realclearpolitics.com/epolls/2020/president/us/general_election_trump_vs_biden-6247.html'}

soup = BeautifulSoup(requests.get("https://www.realclearpolitics.com/epolls/latest_polls/state_president/").text, 'html.parser')
for t in soup.find_all('td', {'class': 'lp-race'}):
	races.add('https://www.realclearpolitics.com' + t.findChild('a').attrs['href'])

for race in races:
	labels = []
	soup = BeautifulSoup(requests.get(race).text, 'html.parser')
	sheet = workbook.add_worksheet('National' if race == 'https://www.realclearpolitics.com/epolls/2020/president/us/general_election_trump_vs_biden-6247.html' else soup.find('h1', {'class': 'page_title'}).string.split(':')[0])
	row = 1
	for t in soup.find_all('div', {'id': 'polling-data-full'}):
		n = 0
		for row in t.findChildren('tr'):
			children = list(row.children)
			if not row.find('td'):
				for i in range(len(children)):
					if children[i].string == 'Poll':
						labels.append('poll')
						sheet.write_string(0, 0, 'Poll')
						sheet.write_string(0, 1, 'Source')
					elif children[i].string == 'Date':
						labels.append('dates')
						sheet.write_string(0, 2, 'Start Date')
						sheet.write_string(0, 3, 'End Date')
					elif children[i].string == 'Sample':
						labels.append('sample')
						sheet.write_string(0, 4, 'Sample Size')
						sheet.write_string(0, 5, 'Sample Type')
					elif children[i].string == 'MoE':
						labels.append('moe')
						sheet.write_string(0, 6, 'MoE')
					elif children[i].string == 'Biden (D)':
						labels.append('biden')
						sheet.write_string(0, 7, 'Biden')
					elif children[i].string == 'Trump (R)':
						labels.append('trump')
						sheet.write_string(0, 8, 'Trump')
				continue
			if 'RCP Average' in str(children[0]): continue
			n += 1
			for i in range(len(labels)):
				if labels[i] == 'poll':
					sheet.write_string(n, 0, children[i].find('a', {'class': 'normal_pollster_name'}).string)
					sheet.write_url(n, 1, children[i].find('a', {'class': 'normal_pollster_name'}).attrs['href'])
				elif labels[i] == 'dates':
					sheet.write_datetime(n, 2, datetime.fromisoformat('2020-'+'-'.join(i.zfill(2) for i in children[i].string.split(' - ')[0].split('/'))), date)
					sheet.write_datetime(n, 3, datetime.fromisoformat('2020-'+'-'.join(i.zfill(2) for i in children[i].string.split(' - ')[1].split('/'))), date)
				elif labels[i] == 'sample':
					try:
						sheet.write_number(n, 4, int(children[i].string.split(' ')[0]))
						sheet.write_string(n, 5, children[i].string.split(' ')[1])
					except ValueError:
						sheet.write_string(n, 5, children[i].string)
				elif labels[i] == 'moe': 
					try: sheet.write_number(n, 6, float(children[i].string))
					except ValueError: pass
				elif labels[i] == 'biden': sheet.write_number(n, 7, float(children[i].string))
				elif labels[i] == 'trump': sheet.write_number(n, 8, float(children[i].string))

workbook.close()
