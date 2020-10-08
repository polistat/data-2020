from datetime import datetime

from bs4 import BeautifulSoup
import csv
import requests

races = {'https://www.realclearpolitics.com/epolls/2020/president/us/general_election_trump_vs_biden-6247.html'}

soup = BeautifulSoup(requests.get("https://www.realclearpolitics.com/epolls/latest_polls/state_president/").text, 'html.parser')
for t in soup.find_all('td', {'class': 'lp-race'}):
	races.add('https://www.realclearpolitics.com' + t.findChild('a').attrs['href'])

with open('polls.csv', 'w', newline='') as f:
	writer = csv.writer(f)
	columns = ['State', 'Poll', 'Source', 'Start Date', 'End Date', 'Sample Size', 'Sample Type', 'MoE', 'Biden', 'Trump']
	writer.writerow(columns)
	for race in races:
		labels = []
		soup = BeautifulSoup(requests.get(race).text, 'html.parser')
		for t in soup.find_all('div', {'id': 'polling-data-full'}):
			for row in t.findChildren('tr'):
				data = ['National' if race == 'https://www.realclearpolitics.com/epolls/2020/president/us/general_election_trump_vs_biden-6247.html' else soup.find('h1', {'class': 'page_title'}).string.split(':')[0].replace(' Polls', '')] + [None]*9
				children = list(row.children)
				if not row.find('td'):
					for i in range(len(children)):
						if children[i].string == 'Poll': labels.append('poll')
						elif children[i].string == 'Date': labels.append('dates')
						elif children[i].string == 'Sample': labels.append('sample')
						elif children[i].string == 'MoE': labels.append('moe')
						elif children[i].string == 'Biden (D)': labels.append('biden')
						elif children[i].string == 'Trump (R)': labels.append('trump')
					continue
				if 'RCP Average' in str(children[0]): continue
				for i in range(len(labels)):
					if labels[i] == 'poll':
						data[1] = children[i].find('a', {'class': 'normal_pollster_name'}).string
						data[2] = children[i].find('a', {'class': 'normal_pollster_name'}).attrs['href']
					elif labels[i] == 'dates':
						data[3] = datetime.fromisoformat('2020-'+'-'.join(i.zfill(2) for i in children[i].string.split(' - ')[0].split('/')))
						data[4] = datetime.fromisoformat('2020-'+'-'.join(i.zfill(2) for i in children[i].string.split(' - ')[1].split('/')))
					elif labels[i] == 'sample':
						try:
							data[5] = int(children[i].string.split(' ')[0])
							data[6] = children[i].string.split(' ')[1]
						except ValueError:
							data[6] = children[i].string
					elif labels[i] == 'moe':
						try: data[7] = float(children[i].string)
						except ValueError: pass
					elif labels[i] == 'biden': data[8] = float(children[i].string)
					elif labels[i] == 'trump': data[9] = float(children[i].string)
				writer.writerow(data)
