import requests
import yaml
import datetime
import pandas as pd
import time
import cx_Oracle
import json

def load_config_file():
        with open('/home/jasper/git/leagueoflegends-optimizer/config.yaml') as file:
                return yaml.safe_load(file)

data = load_config_file()
connection = str()
dsn_var = """(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-frankfurt-1.oraclecloud.com))(connect_data=(service_name=g2f4dc3e5463897_esportsdb_high.adb.oraclecloud.com))(security=(ssl_server_cert_dn="CN=adwc.eucom-central-1.oraclecloud.com, OU=Oracle BMCS FRANKFURT, O=Oracle Corporation, L=Redwood City, ST=California, C=US")))"""
try:
    connection = cx_Oracle.connect(user=data['db']['username'], password=data['db']['password'], dsn=dsn_var)
except Exception as e:
    print('Error in connection.')
    import sys
    sys.exit(-1)

connection.autocommit = True

soda = connection.getSodaDatabase()


collection_matchups = soda.createCollection('matchups')
all_matchups = collection_matchups.find().getDocuments()

data = list()
for x in all_matchups:
    data.append(x.getContent())

print('# Documents: {}'.format(len(data)))
f = open('/home/jasper/Downloads/matchups.json', 'w+')
f.write(str(data))
f.close()

# Read File
df = pd.read_json('/home/jasper/Downloads/matchups.json')

df.info()

print(df.columns)

print(df.describe())