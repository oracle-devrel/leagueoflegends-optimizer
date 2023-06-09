# Copyright (c) 2021 Oracle and/or its affiliates.

import yaml
import cx_Oracle
import os
from pathlib import Path
home = str(Path.home())

def load_config_file():
	with open('../config.yaml') as file:
		return yaml.safe_load(file)


# wallet location (default is HOME/wallets/wallet_X)
os.environ['TNS_ADMIN'] = '{}/{}'.format(home, load_config_file()['WALLET_DIR'])
print(os.environ['TNS_ADMIN'])


def init_db_connection(data):
    connection = cx_Oracle.connect(data['db']['username'], data['db']['password'], data['db']['dsn'])
    print('Connection successful.')
    connection.autocommit = True
    return connection



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
	connection = init_db_connection(data)

	process_1v1_model(connection)
	connection.close()

if __name__ == '__main__':
	main()