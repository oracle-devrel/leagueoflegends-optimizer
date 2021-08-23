import json
import pandas as pd

f = open('../data/champion.json')
data = json.load(f)
#print(data)

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

champion_df.to_csv('../data/champion_ids.csv')

# We make a dictionary with champion names and IDs.