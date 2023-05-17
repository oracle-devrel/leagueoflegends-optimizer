# Copyright (c) 2022 Oracle and/or its affiliates.

'''
@author jasperan
This file uses web sockets to communicate Live Client API data from one endpoint to the other. You can virtually put your consumer 
wherever you want, and let it process the incoming data from the producer.
''' 

from pathlib import Path
import requests
import pandas as pd
import datetime
import argparse
import json 
import websockets
import asyncio
from rich import print


cli_parser = argparse.ArgumentParser()
cli_parser.add_argument('-i', '--ip', type=str, help='IP address to make requests to', required=True)
args = cli_parser.parse_args()

def build_object(content):
    try:
        assert type(content) == type(str())
    except AssertionError:
        return '{}'
    try:
        response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False)
    except requests.exceptions.ConnectionError:
        print('{} | Currently not in game'.format(datetime.datetime.now()))
        return '{}'
    # We convert to JSON format
    content = response.json()
    print('{} {}'.format('x'*5, content))
    for x in content['allPlayers']:
        del x['items'] # delete items to avoid quotation marks

    print('Content: {}'.format(content))
    return content



async def handler(websocket):
    while True:
        message = await websocket.recv()
        print(message)

        if message == 'get_liveclient_data':
            result = build_object(message)
        else:
            result = {}

        await websocket.send(json.dumps(result))




async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
