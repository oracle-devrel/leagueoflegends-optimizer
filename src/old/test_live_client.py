# Copyright (c) 2021 Oracle and/or its affiliates.

import requests
import time
import json
import datetime

while True:
    try:
        response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False)
    except requests.exceptions.ConnectionError:
        # Try again every 5 seconds
        print('{} | Currently not in game'.format(datetime.datetime.now()))
        time.sleep(5)
        continue

    # Send to RabbitMQ queue.
    if response.status_code != 404:
        a = response.json()
        print(json.dumps(a, indent=4))
    time.sleep(30) # wait 30 seconds before making another request