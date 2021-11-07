import os
import yaml
import cx_Oracle
from sys import exit
from pathlib import Path
home = str(Path.home())



def process_yaml():
	with open("../config.yaml") as file:
		return yaml.safe_load(file)



# wallet location (default is HOME/wallets/wallet_X)
os.environ['TNS_ADMIN'] = '{}/{}'.format(home, 'wallets/Wallet_eSportsDB')
print(os.environ['TNS_ADMIN'])



def init_db_connection(data):
	connection = str()
	try:
		connection = cx_Oracle.connect(data['db']['username'], data['db']['password'], 'esportsdb_tpurgent')
		print('Connection successful.')
	except Exception:
		print('Error in connection.')
		exit(-1)
	connection.autocommit = True
	return connection



def main():
    data = process_yaml()
    connection = init_db_connection(data)
    print(connection)



if __name__ == '__main__':
    main()