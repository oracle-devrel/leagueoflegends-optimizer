# Copyright (c) 2021 Oracle and/or its affiliates.

import yaml
import os
from pathlib import Path
import requests
import pandas as pd
import time
import datetime
import pika


_MQ_NAME = 'live_client'

connection = pika.BlockingConnection(
pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue=_MQ_NAME)


def send_message(queue_name, message):
    channel.basic_publish(exchange='', routing_key=queue_name, body='{}'.format(message))
    print('{} | MQ {} OK'.format(datetime.datetime.now(), message))


for x in range(60):
    try:
        response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False)
    except requests.exceptions.ConnectionError:
        # Try again every 5 seconds
        print('{} | Currently not in game'.format(datetime.datetime.now()))
        time.sleep(5)
        continue

    # Send to RabbitMQ queue.
    send_message('live_client', response.json())
    time.sleep(30) # wait 30 seconds before making another request