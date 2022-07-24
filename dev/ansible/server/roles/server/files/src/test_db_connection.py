import os
import yaml
import cx_Oracle
from pathlib import Path
import argparse

# this file tests database connection with the old cx_Oracle library
# now, check out python-oracledb module for more updated functionalities.

# parse arguments for different execution modes.
parser = argparse.ArgumentParser()
parser.add_argument('-w', '--wallet-location', help='Wallet location',
	required=True)
args = parser.parse_args() 

def process_yaml():
	with open("../config.yaml") as file:
		return yaml.safe_load(file)



# wallet location (default is HOME/wallets/wallet_X)
os.environ['TNS_ADMIN'] = args.wallet_location
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