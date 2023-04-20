# Copyright (c) 2022 Oracle and/or its affiliates.


import asyncio
from websockets import connect

import sys, os
from autogluon.tabular import TabularPredictor
import argparse
import pandas as pd
import json
from rich import print
import datetime
import statistics

cli_parser = argparse.ArgumentParser()
cli_parser.add_argument('-p', '--path', type=str, help='Path to predictor.pkl', required=True)
cli_parser.add_argument('-i', '--ip', type=str, help='IP address to make requests to', default='127.0.0.1', required=True)
args = cli_parser.parse_args()

# We load the AutoGluon model.
save_path = args.path  # specifies folder to store trained models

_PREDICTOR = TabularPredictor.load(save_path)
_CURRENT_DATA = str()
_LAST_REQUESTS = list()
_LAST_PROBABILITIES = list()

async def get_info(uri):
    async with connect(uri) as websocket:
        while True:
            await websocket.send("get_liveclient_data")
            message = await websocket.recv()
            #print(message)
            _CURRENT_DATA = message
            process_and_predict(_CURRENT_DATA)




def main():
    asyncio.run(get_info('ws://{}:8001'.format(args.ip)))



def process_and_predict(input):

    json_obj = json.loads(input)
    team_color = str()
    try:
        json_obj['allPlayers']
    except (KeyError, TypeError):
        return
    for x in json_obj['allPlayers']:
        if x['team'] == 'ORDER' and x['isBot'] == False:
            team_color = 'blue'
            break
        elif x['team'] == 'CHAOS' and x['isBot'] == False:
            team_color = 'red'
            break
        
    # Timestamp given by the Live Client API is in thousands of a second from the starting point.

    timestamp = int(json_obj['gameData']['gameTime'] * 1000)
    data = [
        json_obj['activePlayer']['championStats']['magicResist'],
        json_obj['activePlayer']['championStats']['healthRegenRate'],
        json_obj['activePlayer']['championStats']['spellVamp'],
        timestamp,
        json_obj['activePlayer']['championStats']['maxHealth'],
        json_obj['activePlayer']['championStats']['moveSpeed'],
        json_obj['activePlayer']['championStats']['attackDamage'],
        json_obj['activePlayer']['championStats']['armorPenetrationPercent'],
        json_obj['activePlayer']['championStats']['lifeSteal'],
        json_obj['activePlayer']['championStats']['abilityPower'],
        json_obj['activePlayer']['championStats']['resourceValue'],
        json_obj['activePlayer']['championStats']['magicPenetrationFlat'],
        json_obj['activePlayer']['championStats']['attackSpeed'],
        json_obj['activePlayer']['championStats']['currentHealth'],
        json_obj['activePlayer']['championStats']['armor'],
        json_obj['activePlayer']['championStats']['magicPenetrationPercent'],
        json_obj['activePlayer']['championStats']['resourceMax'],
        json_obj['activePlayer']['championStats']['resourceRegenRate']
    ]
    columns=['magicResist', 'healthRegenRate', 'spellVamp', 'timestamp', 'maxHealth',
        'moveSpeed', 'attackDamage', 'armorPenetrationPercent', 'lifesteal', 'abilityPower', 'resourceValue', 'magicPenetrationFlat',
        'attackSpeed', 'currentHealth', 'armor', 'magicPenetrationPercent', 'resourceMax', 'resourceRegenRate']
    column_names = [x.upper() for x in columns]

    sample_df = pd.DataFrame([data], columns = column_names)
    prediction = _PREDICTOR.predict(sample_df)
    pred_probs = _PREDICTOR.predict_proba(sample_df)

    expected_result = prediction.get(0)


    if len(_LAST_REQUESTS) > 100:
        _LAST_REQUESTS.pop(0)
    if len(_LAST_PROBABILITIES) > 100:
        _LAST_PROBABILITIES.pop(0)

    _LAST_REQUESTS.append(expected_result)
    _LAST_PROBABILITIES.append(pred_probs.iloc[0][1] * 100) # winning probabilities are stored

    list_mode = int()
    try:
        list_mode = statistics.mode(_LAST_REQUESTS)
    except ValueError as e:
        print(e)
        return
    info = {
        '100_average_prediction': list_mode,
        '100_average_probability': '{:.2f}'.format(sum(_LAST_PROBABILITIES)/len(_LAST_PROBABILITIES))
    }
    print('[bold {}]TEAM {}[/bold {}] [{}]: {}'.format(team_color,
        team_color.upper(),
        team_color,
        datetime.datetime.now(),
        info)
    ) # 1 = WIN, 0 = LOSS

    return expected_result, pred_probs.iloc[0][1], pred_probs.iloc[0][0] # expected_result(1=win, 0=loss), win %, loss %



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)