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
	collection_detail = soda.createCollection('match_detail')
	print('Collection {} has {} documents left to process'.format('match', collection.find().filter({'processed_1v1': {'$ne': 1}}).count()))
	print('Collection {} [CLASSIFIER_PROCESSED]: {}/{} ({}%)'.format('match_detail', collection_detail.find().filter({'classifier_processed': {'$eq': 1}}).count(),
	collection_detail.find().count(), (collection_detail.find().filter({'classifier_processed': {'$eq': 1}}).count()/collection_detail.find().count())*100))
	print('Collection {} [CLASSIFIER_PROCESSED_LIVECLIENT]: {}/{} ({}%)'.format('match_detail', collection_detail.find().filter({'classifier_processed_liveclient': {'$eq': 1}}).count(),
	collection_detail.find().count(), (collection_detail.find().filter({'classifier_processed_liveclient': {'$eq': 1}}).count()/collection_detail.find().count())*100))

def main():
	data = process_yaml()
	conn = init_db_connection(data)
	
	for x in conn.getSodaDatabase().getCollectionNames(startName=None, limit=0):
		find_counts(x, conn) # find all documents in every collection.
	find_remaining_matches_to_process(conn)


if __name__ == '__main__':
	main()