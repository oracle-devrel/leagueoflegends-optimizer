# Copyright (c) 2021 Oracle and/or its affiliates.

import requests
import yaml

def load_config_file():
	with open('../config.yaml') as file:
		return yaml.safe_load(file)

config_file = load_config_file()
api_key = config_file.get('riot_api_key')

