#!/usr/bin/env python
import re
import pika, sys, os
import datetime
from autogluon.tabular import TabularPredictor, TabularDataset
import argparse
import pandas as pd
from pika.credentials import PlainCredentials
import json

cli_parser = argparse.ArgumentParser()
cli_parser.add_argument('-p', '--path', type=str, help='Path to predictor.pkl', required=True)
cli_parser.add_argument('-i', '--ip', type=str, help='IP address to make requests to', required=True)
args = cli_parser.parse_args()

# We load the AutoGluon model.
save_path = args.path  # specifies folder to store trained models
_PREDICTOR = TabularPredictor.load(save_path)


def main():

    try:

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        # declare queue, in case the receiver is initialized before the producer.
        channel.queue_declare(queue='live_client')

        def callback(ch, method, properties, body):
            print('{} | MQ Received {}'.format(datetime.datetime.now(), body.decode()))
            process_and_predict(body.decode())

        # consume queue
        channel.basic_consume(queue='live_client', on_message_callback=callback, auto_ack=True)
        
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    except pika.exceptions.StreamLostError:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))



def process_and_predict(input):

    json_obj = json.loads(input)

    '''
    print('{} | Level {} | Current stats: {}'.format(json_obj['activePlayer']['summonerName'], 
        json_obj['activePlayer']['level'],
        json_obj['activePlayer']['championStats']))
    '''
    print('{} | Level {}'.format(json_obj['activePlayer']['summonerName'], 
        json_obj['activePlayer']['level']))

    team_color = str()
    for x in json_obj['allPlayers']:
        if x['team'] == 'ORDER':
            team_color = 'blue'
        else:
            team_color = 'red'
        
        print('Team {}: {}'.format(team_color, x['championName']))

    # Timestamp given by the Live Client API is in thousands of a second from the starting point. (assumption)

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


    sample_df = pd.DataFrame([data], columns=['magicResist', 'healthRegenRate', 'spellVamp', 'timestamp', 'maxHealth',
        'moveSpeed', 'attackDamage', 'armorPenetrationPercent', 'lifesteal', 'abilityPower', 'resourceValue', 'magicPenetrationFlat',
        'attackSpeed', 'currentHealth', 'armor', 'magicPenetrationPercent', 'resourceMax', 'resourceRegenRate'])
    prediction = _PREDICTOR.predict(sample_df)
    pred_probs = _PREDICTOR.predict_proba(sample_df)
    print('User expected result: {} | Probability: {}'.format(prediction, pred_probs))
    


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)