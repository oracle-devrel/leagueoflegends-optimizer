import yaml
import cx_Oracle
import time


def process_yaml():
	with open("../config.yaml") as file:
		return yaml.safe_load(file)



def create_connection(data):
	connection = str()
	dsn_var = """(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-frankfurt-1.oraclecloud.com))(connect_data=(service_name=g2f4dc3e5463897_esportsdb_high.adb.oraclecloud.com))(security=(ssl_server_cert_dn="CN=adwc.eucom-central-1.oraclecloud.com, OU=Oracle BMCS FRANKFURT, O=Oracle Corporation, L=Redwood City, ST=California, C=US")))"""
	try:
		connection = cx_Oracle.connect(user=data['db']['username'], password=data['db']['password'], dsn=dsn_var)
	except cx_Oracle.DatabaseError:
		print('Error in connection.')
		time.sleep(1)
		connection = cx_Oracle.connect(user=data['db']['username'], password=data['db']['password'], dsn=dsn_var)

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
	conn = create_connection(data)
	for x in ['match', 'matchups', 'summoner', '1v1_model']:
		find_counts(x, conn)
	find_remaining_matches_to_process(conn)

if __name__ == '__main__':
	main()