import csv
import urllib.request
import collections

reader = csv.DictReader([line.decode('utf-8') for line in urllib.request.urlopen('https://projects.fivethirtyeight.com/polls-page/president_polls.csv').readlines()])

columns = ['State', 'Poll', 'Source', 'Start Date', 'End Date', 'Sample Size', 'Sample Type', 'Biden', 'Trump']
polls = collections.defaultdict(lambda: [None]*9)

for result in reader:
	poll = polls[result['poll_id']]
	if not poll[6] and result['population'] in ('rv', 'lv') or poll[6] != 'rv' and result['population'] == 'rv' or poll[6] == result['population']:
		if not ('A' in result['fte_grade'] or 'B' in result['fte_grade'] or 'C' in result['fte_grade']): continue
		poll[0] = result['state']
		poll[1] = result['pollster']
		poll[2] = result['url']
		poll[3] = result['start_date']
		poll[4] = result['end_date']
		poll[5] = result['sample_size']
		poll[6] = result['population']
		if result['candidate_id'] == '13256': polls[result['poll_id']][7] = result['pct']
		elif result['candidate_id'] == '13254': polls[result['poll_id']][8] = result['pct']

writer = csv.writer(open('538.csv', 'w', newline=''))
writer.writerow(columns)
writer.writerows(filter(lambda p: p[0], polls.values()))
