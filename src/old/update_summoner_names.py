# Copyright (c) 2021 Oracle and/or its affiliates.

# this file uses a database connection with the old cx_Oracle library
# now, check out python-oracledb module for more updated functionalities.


# This code updates the summoner names given their encrypted summoner Ids.
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



api_key = process_yaml()['riot_api_key']
request_regions = ['br1', 'eun1', 'euw1', 'jp1', 'kr', 'la1', 'la2', 'na1', 'oc1', 'ru', 'tr1']
# TAGLINES:
# BR1, EUNE, EUW, JP1, KR, LA1, LA2, NA, OCE, RU, TR

# oce, NA, TR? still missing to test. most cases it's uppercase the request_region in summoner except EUW1 which is EUW and EUN1 which is EUNE.

# americas, asia, esports, europe
# americas: BR1
# europe: EUW, EUNE
# asia: JP1

# TODO