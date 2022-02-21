# Copyright (c) 2021 Oracle and/or its affiliates.

import yaml
import os
from pathlib import Path
import requests
import pandas as pd
import time
import datetime
import pika
import argparse
from pika.credentials import PlainCredentials

cli_parser = argparse.ArgumentParser()
cli_parser.add_argument('-i', '--ip', type=str, help='IP address to make requests to', required=True)
args = cli_parser.parse_args()

_MQ_NAME = 'live_client'

credentials = PlainCredentials('league', 'league')
connection = pika.BlockingConnection(
pika.ConnectionParameters(
    '{}'.format(args.ip),
    5672,
    '/',
    credentials))
channel = connection.channel()

channel.queue_declare(queue=_MQ_NAME)


def send_message(queue_name, message):
    channel.basic_publish(exchange='', routing_key=queue_name, body='{}'.format(message))
    print('{} | MQ {} OK'.format(datetime.datetime.now(), message))


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
        send_message('live_client', response.json())
    time.sleep(30) # wait 30 seconds before making another request