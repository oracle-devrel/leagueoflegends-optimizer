# Copyright (c) 2021 Oracle and/or its affiliates.

import requests
import yaml
import datetime
import pandas as pd
import time
import cx_Oracle

request_regions = ['br1', 'eun1', 'euw1', 'jp1', 'kr', 'la1', 'la2', 'na1', 'oc1', 'ru', 'tr1']

def load_config_file():
	with open('../config.yaml') as file:
		return yaml.safe_load(file)

config_file = load_config_file()
api_key = config_file.get('riot_api_key')
headers = {
	"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
	"Accept-Language": "en-US,en;q=0.5",
	"Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
	"Origin": "https://developer.riotgames.com",
	"X-Riot-Token": api_key
}

# 1000 requests per minute using development key
# AK89OMWJzaal2SSLDtQszoKUZ220Akz0JppfTK6pF97VYve_KQEHcA9RdEx88ghXl_SbW6Nfpj2xyg
def get_puuid(request_ref, summoner_name, region, connection):
	request_url = 'https://{}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}'.format(request_ref, summoner_name, region) # europe, JASPERAN, EUW

	response = requests.get(request_url, headers=headers)
	time.sleep(1)
	if response.status_code == 200:
		#print('Printing response for user {} - region {}: -----\n{}'.format(summoner_name, region, response.json()))
		pass
	elif response.status_code == 404:
		print('PUUID not found for summoner {}'.format(summoner_name))
		delete_json_db(connection, 'summoner', 'summonerName', summoner_name)
	else:
		print('Request error (@get_puuid). HTTP code {}'.format(response.status_code))
		return
	puuid = response.json().get('puuid')
	return puuid



# encrypted summoner ID: y8zda_vuZ5AkVYk8yXJrHa_ppKjIblOGKPCwzYcX9ywo4G0
# will return the PUUID but can be changed to return anything.
def get_summoner_information(summoner_name, request_region):
	assert request_region in request_regions

	request_url = 'https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}'.format(request_region, summoner_name)
	
	response = requests.get(request_url, headers=headers)
	if response.status_code != 200:
		print('Request error (@get_summoner_information). HTTP code {}'.format(response.status_code))
		return None
	return response.json().get('puuid')



def get_champion_mastery(encrypted_summoner_id, request_region):
	assert request_region in request_regions

	request_url = 'https://{}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{}'.format(request_region, encrypted_summoner_id)
	
	response = requests.get(request_url, headers=headers)
	if response.status_code == 200:
		print('{}'.format(response.json()))
	else:
		print('Request error (@get_champion_mastery). HTTP code {}'.format(response.status_code))
	
	# Get champion IDs
	champion_df = pd.read_csv('../data/champion_ids.csv')
	
	# Example: get champion name by its id.
	#print(champion_df.loc[champion_df['champion_id'] == 103])
	# Processing of the information
	print('Total champions played: {}'.format(len(response.json())))
	for i in response.json():
		champion_name = champion_df.loc[champion_df['champion_id'] == i.get('championId')]['champion_name'].to_string().split('    ')[1] # get the champion name only
		print('Champion ID {} | Champion Name {} | Mastery level {} | Total mastery points {} | Last time played {} | Points until next mastery level {} | Chest granted {} | Tokens earned {}'.format(
				i.get('championId'),
				champion_name,
				i.get('championLevel'),
				i.get('championPoints'),
				datetime.datetime.fromtimestamp(i.get('lastPlayTime')/1000).strftime('%c'),
				i.get('championPointsUntilNextLevel'),
				i.get('chestGranted'),
				i.get('tokensEarned')))



def get_total_champion_mastery_score(encrypted_summoner_id, request_region):
	assert request_region in request_regions
	request_url = 'https://{}.api.riotgames.com/lol/champion-mastery/v4/scores/by-summoner/{}'.format(request_region, encrypted_summoner_id)
	
	response = requests.get(request_url, headers=headers)
	if response.status_code == 200:
		print('{}'.format(response.json()))
	else:
		print('Request error (@get_total_champion_mastery_score). HTTP code {}'.format(response.status_code))



def get_user_leagues(encrypted_summoner_id, request_region):
	assert request_region in request_regions
	request_url = 'https://{}.api.riotgames.com/lol/league/v4/entries/by-summoner/{}'.format(request_region, encrypted_summoner_id)
	
	response = requests.get(request_url, headers=headers)
	if response.status_code == 200:
		print('{}'.format(response.json()))
	else:
		print('Request error (@get_user_leagues). HTTP code {}'.format(response.status_code))

	for i in response.json():
		if i.get('leaguePoints') != 100:
			print('Queue type: {} | Rank: {} {} {} LP | Winrate: {}% | Streak {} | >100 games {} | Inactive {}'.format(
				i.get('queueType'),
				i.get('tier'),
				i.get('rank'),
				i.get('leaguePoints'),
				(i.get('wins') / (i.get('losses') + i.get('wins'))) * 100,
				i.get('hotStreak'),
				i.get('veteran'),
				i.get('inactive')))
		else:
			print('Queue type: {} | Rank: {} {} {} LP - Promo standings: {}/{} | Winrate: {}% | Streak {} | >100 games {} | Inactive {}'.format(
				i.get('queueType'),
				i.get('tier'),
				i.get('rank'),
				i.get('leaguePoints'),
				i.get('miniSeries').get('wins'),
				i.get('miniSeries').get('losses'),
				(i.get('wins') / (i.get('losses') + i.get('wins'))) * 100,
				i.get('hotStreak'),
				i.get('veteran'),
				i.get('inactive')))



def get_n_match_ids(puuid, num_matches, queue_type, region):
	available_regions = ['europe', 'americas', 'asia']
	queue_types = ['ranked', 'tourney', 'normal', 'tutorial']
	assert region in available_regions
	assert queue_type in queue_types
	assert num_matches in range(0, 991)
	returning_object = list()
	iterator = 0
	request_url = 'https://{}.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?type={}&start={}&count={}'.format(
		region,
		puuid,
		queue_type,
		iterator,
		100
	)
	
	for x in range(int(num_matches / 100)):
		response = requests.get(request_url, headers=headers)
		time.sleep(1)
		if response.status_code != 200:
			print('Request error (@get_n_match_ids). HTTP code {}: {}'.format(response.status_code, response.json()))
		# Return the list of matches.
		for i in response.json():
			returning_object.append(
				{
					'match_id':i
				}
			)
		# Modify the next request_url.
		iterator = iterator + 100
		request_url = 'https://{}.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?type={}&start={}&count={}'.format(
			region,
			puuid,
			queue_type,
			iterator,
			100
		)
	print('@get_n_match_ids: obtained {} matches from region {}'.format(len(returning_object), region))
	return returning_object


# This has a ridiculous amount of information. (see ../data/get_match_timeline.json)
def get_match_timeline(match_id, region):
	available_regions = ['europe', 'americas', 'asia']
	assert region in available_regions
	request_url = 'https://{}.api.riotgames.com/lol/match/v5/matches/{}/timeline'.format(
		region,
		match_id
	)
	
	response = requests.get(request_url, headers=headers)
	if response.status_code == 200:
		print('{}'.format(response.json()))
	else:
		print('Request error (@get_match_timeline). HTTP code {}'.format(response.status_code))
	# Return the list of matches.
	return response.json()




def get_match_info(match_id, region):
	available_regions = ['europe', 'americas', 'asia']
	assert region in available_regions
	request_url = 'https://{}.api.riotgames.com/lol/match/v5/matches/{}'.format(
		region,
		match_id
	)
	
	response = requests.get(request_url, headers=headers)
	if response.status_code == 200:
		print('{}'.format(response.json()))
	else:
		print('Request error (@get_match_info). HTTP code {}'.format(response.status_code))
	# Return the list of matches.
	return response.json()



# auxiliary function
def determine_overall_region(region):
	overall_region = str()
	tagline = str()
	if region in ['euw1', 'eun1', 'ru', 'tr1']:
		overall_region = 'europe'
	elif region in ['br1', 'la1', 'la2', 'na1']:
		overall_region = 'americas'
	else:
		overall_region = 'asia'
	# BR1, EUNE, EUW, JP1, KR, LA1, LA2, NA, OCE, RU, TR
	if region in ['br1', 'jp1', 'kr', 'la1', 'la2', 'ru', 'na1', 'tr1', 'oc1']:
		tagline = region.upper()
	elif region == 'euw1':
		tagline = 'EUW'
	elif region == 'eun1':
		tagline = 'EUNE'
	# 3 cases left: OCE
	return overall_region, tagline



# auxiliary function
def insert_json_db(connection, collection_name, json_object_to_insert):
	soda = connection.getSodaDatabase()
	x_collection = soda.createCollection(collection_name)

	try:
		x_collection.insertOne(json_object_to_insert)
	except cx_Oracle.IntegrityError:
		return 0
	return 1



# auxiliary function
def delete_json_db(connection, collection_name, on_column, on_value):
	soda = connection.getSodaDatabase()
	x_collection = soda.createCollection(collection_name)

	qbe = {on_column: on_value}
	x_collection.find().filter(qbe).remove()



def get_top_players(region, queue, connection):
	assert region in request_regions
	assert queue in ['RANKED_SOLO_5x5', 'RANKED_FLEX_SR', 'RANKED_FLEX_TT']

	total_users_to_insert = list()
	# master, grandmaster and challenger endpoints
	
	request_urls = [
		'https://{}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/{}'.format(
			region,
			queue
		),
		'https://{}.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/{}'.format(
			region,
			queue
		),
		'https://{}.api.riotgames.com/lol/league/v4/masterleagues/by-queue/{}'.format(
			region,
			queue
		)
	]

	for x in request_urls:
		response = requests.get(x, headers=headers)
		if response.status_code == 200:
			try:
				print('Region: {} | Tier: {} | Queue: {} | Total Players: {}'.format(region, response.json()['tier'],
					response.json()['queue'], len(response.json()['entries'])))
			except KeyError:
				pass
			for y in response.json()['entries']:
				try:
					y['tier'] = response.json()['tier']
					y['request_region'] = region
					y['queue'] = queue
					total_users_to_insert.append(y)
				except KeyError:
					pass
		else:
			print('Request error (@get_top_players). HTTP code {}: {}'.format(response.status_code, response.json()))

	print('Total users obtained in region {} and queue {}: {}'.format(region, queue, len(total_users_to_insert)))
	
	# Insert into the database.
	soda = connection.getSodaDatabase()
	collection_summoner = soda.createCollection('summoner')

	# Insert the users.
	for x in total_users_to_insert:
		x['request_region'] = region
		x['queue'] = queue
		try:
			qbe = {'summonerId':x['summonerId']}
			if len(collection_summoner.find().filter(qbe).getDocuments()) == 0:
				# In case they don't exist in the DB, we get their PUUIDs, in case they change their name.
				overall_region, tagline = determine_overall_region(region)
				x['puuid'] = get_puuid(overall_region, x['summonerName'], tagline, connection)
				collection_summoner.insertOne(x)
				print('Inserted new summoner: {} in region {}, queue {}'.format(x['summonerName'], region, queue))
			else:
				print('Summoner {} already inserted'.format(x['summonerName']))
				continue
		except cx_Oracle.IntegrityError:
			print('Summoner {} already inserted'.format(x['summonerName']))
			continue
	



def extract_matches(region, match_id, connection):
	available_regions = ['europe', 'americas', 'asia']
	assert region in available_regions
	request_url = 'https://{}.api.riotgames.com/lol/match/v5/matches/{}'.format(
		region,
		match_id
	)
	
	response = requests.get(request_url, headers=headers)
	time.sleep(1.5) # rate limiting purposes
	if response.status_code != 200:
		print('Request error (@extract_matches). HTTP code {}'.format(response.status_code))
		return
	# Get participants and teams.objectives objects
	o_version = response.json().get('info').get('gameVersion')
	o_participants = response.json().get('info').get('participants') 
	o_teams = response.json().get('info').get('teams')

	matchups = {
		'top':list(),
		'middle':list(),
		'bottom':list(),
		'utility':list(),
		'jungle':list()
	}
	# Extract individual matchups
	for x in o_participants:
		try:
			matchups['{}'.format(x.get('individualPosition').lower())].append(
				{
					'champion': x.get('championName'),
					'assists': x.get('assists'),
					'deaths': x.get('deaths'),
					'goldEarned': x.get('goldEarned'),
					'kills': x.get('kills'),
					'puuid': x.get('puuid'),
					'summonerName': x.get('summonerName'),
					'totalDamageDealtToChampions': x.get('totalDamageDealtToChampions'),
					'totalMinionsKilled': x.get('totalMinionsKilled'),
					'visionScore': x.get('visionScore'),
					'win': x.get('win')
				}
			)
		except KeyError:
			# Then we have an Invalid position detected (probably AFK). In this case, we ignore it.
			continue
	# Check lengths to see if any lanes had invalid matchups. In this case, remove them.
	for x, y in matchups.items():
		if len(y) != 2:
			#print('[ERR] Detected error in {} lane'.format(x))
			continue
		else:
			# We insert our matchups info into the db
			soda = connection.getSodaDatabase()
			collection_matchups = soda.createCollection('matchups')

			# Check which of these are not present.
			match_id = response.json().get('metadata').get('matchId')
			to_insert_obj = {
				'p_match_id': '{}_{}'.format(match_id, x),
				'data': y,
				'gameVersion': o_version
			}
			try:
				collection_matchups.insertOne(to_insert_obj)
			except cx_Oracle.IntegrityError:
				print('Match details {} already inserted'.format(to_insert_obj.get('p_match_id')))
				continue
			print('Inserted new matchup with ID {} in region {}'.format('{}_{}'.format(match_id, x), region))

	# Now, set a processed_1v1 bit in the match
	collection_match = connection.getSodaDatabase().createCollection('match')
	match_document = collection_match.find().filter({'match_id': match_id}).getOne()
	match_key = match_document.key
	match_obj = match_document.getContent()
	match_obj['processed_1v1'] = 1
	collection_match.find().key(match_key).replaceOne(match_obj)

	return response.json()



def data_mine(connection):
	'''
	# Get top players from API and add them to our DB.
	for x in request_regions:
		for y in ['RANKED_SOLO_5x5', 'RANKED_FLEX_SR']: # RANKED_FLEX_TT disabled since the map was removed
			get_top_players(x, y, connection)
	
	# ------
	'''
	# From all users in the collection, extract matches
	all_match_ids = list()
	soda = connection.getSodaDatabase()
	collection_summoner = soda.createCollection('summoner')
	collection_match = soda.createCollection('match')
	'''
	all_summoners = collection_summoner.find().getDocuments()
	
	for x in all_summoners:
		current_summoner = x.getContent()
		current_summoner_puuid = get_summoner_information(current_summoner['summonerName'], current_summoner['request_region'])
		if current_summoner_puuid is None:
			continue
		for y in ['europe', 'americas', 'asia']:
			for z in ['ranked', 'tourney']:
				z_match_ids = get_n_match_ids(current_summoner_puuid, 990, z, y)
				# Insert them into our match collection	
				for i in z_match_ids:
					try:
						collection_match.insertOne(i)
					except cx_Oracle.IntegrityError:
						print('Match ID {} already inserted'.format(i))
						continue
					print('Inserted new match with ID {} from summoner {} in region {}, queue {}'.format(i['match_id'],
						current_summoner['summonerName'], y, z))
	
	# We have the match IDs, let's get some info about the games.
	'''
	all_match_ids = collection_match.find().filter({'processed_1v1': {"$ne":1}}).getDocuments()
	for x in all_match_ids:
		# Get the overall region to make the proper request
		overall_region, tagline = determine_overall_region(x.getContent().get('match_id').split('_')[0].lower())
		print('Overall Region {} detected'.format(overall_region))
		extract_matches(overall_region, x.getContent().get('match_id'), connection)	




def main():
	data = load_config_file()
	connection = str()
	dsn_var = """(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-frankfurt-1.oraclecloud.com))(connect_data=(service_name=g2f4dc3e5463897_esportsdb_high.adb.oraclecloud.com))(security=(ssl_server_cert_dn="CN=adwc.eucom-central-1.oraclecloud.com, OU=Oracle BMCS FRANKFURT, O=Oracle Corporation, L=Redwood City, ST=California, C=US")))"""
	try:
		connection = cx_Oracle.connect(user=data['db']['username'], password=data['db']['password'], dsn=dsn_var)
	except Exception as e:
		print('Error in connection.')
		connection = cx_Oracle.connect(user=data['db']['username'], password=data['db']['password'], dsn=dsn_var)

	connection.autocommit = True

	data_mine(connection)
	connection.close()

if __name__ == '__main__':
	main()