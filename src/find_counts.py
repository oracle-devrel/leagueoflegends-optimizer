import yaml
import cx_Oracle
import os
from pathlib import Path
home = str(Path.home())

def process_yaml():
	with open("../config.yaml") as file:
		return yaml.safe_load(file)



# wallet location (default is HOME/wallets/wallet_X)
os.environ['TNS_ADMIN'] = '{}/{}'.format(home, process_yaml()['WALLET_DIR'])
print(os.environ['TNS_ADMIN'])



def init_db_connection(data):
    connection = cx_Oracle.connect(data['db']['username'], data['db']['password'], data['db']['dsn'])
    print('Connection successful.')
    connection.autocommit = True
    return connection



def find_counts(collection_name, connection):
	soda = connection.getSodaDatabase()
	collection = soda.createCollection(collection_name)
	print('Collection {} has {} documents'.format(collection_name, collection.find().count()))



def find_remaining_matches_to_process(connection):
	soda = connection.getSodaDatabase()
	collection = soda.createCollection('match')
	print('Collection {} has {} documents left to process'.format('match', collection.find().filter({'processed_1v1': {'$ne': 1}}).count()))



def main():
	data = process_yaml()
	conn = init_db_connection(data)
	for x in ['match', 'matchups', 'summoner', '1v1_model']:
		find_counts(x, conn)
	find_remaining_matches_to_process(conn)



if __name__ == '__main__':
	main()