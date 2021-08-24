# Copyright (c) 2021 Oracle and/or its affiliates.

import json
import os
import pandas as pd
import requests

current_version = '11.14.1' # change this depending on the current game version, or the game version you want to process.
request_url = 'http://ddragon.leagueoflegends.com/cdn/{}/data/en_US/champion.json'.format(current_version)

headers = {
		"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
		"Accept-Language": "en-US,en;q=0.5",
		"Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8"
}
response = requests.get(request_url, headers=headers)


data = response.json()

print(len(data))

print('Version: {}'.format(data.get('version')))

champions = data.get('data')

print('Total champions: {}'.format(len(champions)))

#print(champions.get('Aatrox'))


ids, keys, titles = (list(), list(), list())


for key, value in champions.items():
	#print('{}, {}: {}'.format(value.get('id'), value.get('title'), value.get('key')))
	ids.append(value.get('id')), keys.append(value.get('key')), titles.append(value.get('title'))
	print('{}\t{}'.format(value.get('id'), value.get('key')))
	print('Stats: {}'.format(value.get('stats')))

champion_df = {
	'champion_name':ids,
	'champion_title':titles,
	'champion_id':keys,
}
champion_df = pd.DataFrame(champion_df)

champion_df.index.name = 'index'


print(champion_df)

if os.path.exists('../../champion_ids.csv'):
	champion_df.to_csv('../../champion_ids.csv')
else:
	f = open('../../champion_ids.csv', 'w+')
	f.write()
	champion_df.to_csv('../../champion_ids.csv')

# We make a dictionary with champion names and IDs.