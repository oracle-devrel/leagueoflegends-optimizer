# Copyright (c) 2021 Oracle and/or its affiliates.

import yaml
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



config_file = process_yaml()
api_key = config_file.get('riot_api_key')

# TODO
