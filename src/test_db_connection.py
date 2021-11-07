import os
import yaml
import cx_Oracle
from pathlib import Path
home = str(Path.home())



def process_yaml():
	with open("../config.yaml") as file:
		return yaml.safe_load(file)



# wallet location (default is HOME/wallets/wallet_X)
os.environ['TNS_ADMIN'] = '{}/{}'.format(home, 'wallets/Wallet_eSportsDB')
print(os.environ['TNS_ADMIN'])



def init_db_connection(data):
    connection = cx_Oracle.connect(data['db']['username'], data['db']['password'], data['db']['dsn'])
    print('Connection successful.')
    connection.autocommit = True
    return connection



def main():
    data = process_yaml()
    connection = init_db_connection(data)
    print(connection)



if __name__ == '__main__':
    main()