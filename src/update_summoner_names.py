# This code updates the summoner names given their encrypted summoner Ids.
import requests
import yaml
import datetime
import pandas as pd
import time
import cx_Oracle

def load_config_file():
	with open('../config.yaml') as file:
		return yaml.safe_load(file)

config_file = load_config_file()
api_key = config_file.get('riot_api_key')

request_regions = ['br1', 'eun1', 'euw1', 'jp1', 'kr', 'la1', 'la2', 'na1', 'oc1', 'ru', 'tr1']
# TAGLINES:
# BR1, EUNE, EUW, JP1, KR, LA1, LA2, NA, OCE, RU, TR

# oce, NA, TR? still missing to test. most cases it's uppercase the request_region in summoner except EUW1 which is EUW and EUN1 which is EUNE.

# americas, asia, esports, europe
# americas: BR1
# europe: EUW, EUNE
# asia: JP1