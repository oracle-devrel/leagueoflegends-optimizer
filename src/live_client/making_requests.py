# Copyright (c) 2021 Oracle and/or its affiliates.

import requests
import time
import datetime
import json 
import urllib3

urllib3.disable_warnings()



def build_object(content):
    # We convert to JSON format
    content = response.json()
    for x in content['allPlayers']:
        del x['items'] # delete items to avoid quotation marks
    built_obj = {
        'activePlayer': content['activePlayer'],
        'allPlayers': content['allPlayers']
    }
    content = json.dumps(content)
    content = content.replace("'", "\"")
    print(content)
    return content



while True:
    try:
        response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False)
    except requests.exceptions.ConnectionError:
        # Try again every 5 seconds
        print('{} | Currently not in game'.format(datetime.datetime.now()))
        time.sleep(5)
        continue

    # Display result
    if response.status_code != 404:
        build_object(response.content)
    time.sleep(10) # wait 10 seconds before making another request