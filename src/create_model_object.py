# Copyright (c) 2021 Oracle and/or its affiliates.

import requests
import yaml
import datetime
import pandas as pd
import time
import cx_Oracle
import random

def load_config_file():
	with open('../config.yaml') as file:
		return yaml.safe_load(file)

def process_1v1_model(connection):
	
	# Now, set a processed_1v1 bit in the match
	collection_matchups = connection.getSodaDatabase().createCollection('matchups')
	collection_1v1_model = connection.getSodaDatabase().createCollection('1v1_model')
	matchup_documents = collection_matchups.find().getDocuments()

	for x in matchup_documents:
	#shuffled_list = random.shuffle(matchup_documents)
		match_id = x.getContent().get('p_match_id')
		data = x.getContent().get('data')
		champion_matchup = list()
		win_matchup = list()
		for y in data:
			champion_matchup.append(y.get('champion'))
			win_matchup.append(y.get('win'))
			win_var = int()
			if win_matchup[0] is True:
				win_var = 1
			else: 
				win_var = 0
		obj = {
			'match_id':match_id,
			'champ1':champion_matchup[0],
			'champ2':champion_matchup[1],
			'win': win_var
		}
		print(obj)
		try:
			collection_1v1_model.insertOne(obj)
		except cx_Oracle.IntegrityError:
			continue
		print('Inserted {}'.format(obj))


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

	process_1v1_model(connection)
	connection.close()

if __name__ == '__main__':
	main()