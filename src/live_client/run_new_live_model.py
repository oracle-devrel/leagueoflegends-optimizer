# Copyright (c) 2021 Oracle and/or its affiliates.

import requests
import time
import datetime
import json 
import urllib3
from autogluon.tabular import TabularDataset, TabularPredictor
import pandas as pd
from rich import print
# https://stackoverflow.com/questions/57286486/i-cant-load-my-model-because-i-cant-put-a-posixpath
import pathlib
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath
urllib3.disable_warnings()

 
import argparse

# you can specify your model path here, 
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-m', '--model_path', type=str, help='path to the trained model',
                    required=False,
                    default="H:/Downloads/live1/",
                )
args = parser.parse_args()




def build_object(content):
    # We convert to JSON format
    content = response.json()
    for x in content['allPlayers']:
        del x['items'] # delete items to avoid quotation marks
    built_obj = {
        'activePlayer': content['activePlayer'],
        'allPlayers': content['allPlayers'],
        'gameData': content['gameData']
    }
    content = json.dumps(content)
    content = content.replace("'", "\"")
    #print('OK {}'.format(content))
    return built_obj

'''
    'duration': duration_m,
    'f1': deaths_per_min,
    'f2': k_a_per_min,
    'f3': level_per_min,
    'f4': total_damage_per_min,
    'f5': gold_per_min,
'''
def parse_object(obj):
    #print(obj['gameData']['gameTime'])
    duration = obj['gameData']['gameTime'] / 60 # get duration in minutes

    deaths_per_min = obj['allPlayers'][0]['scores']['deaths'] / duration
    k_a_per_min = (obj['allPlayers'][0]['scores']['kills'] + obj['allPlayers'][0]['scores']['assists']) / duration
    level_per_min = obj['activePlayer']['level'] / duration

    f1 = deaths_per_min
    f2 = k_a_per_min
    f3 = level_per_min


    relevant_data = {
        'championName': obj['allPlayers'][0]['championName'],
        'f1': f1,
        'f2': f2,
        'f3': f3,
        'duration': duration
    }

    #print(relevant_data)

    #obj['activePlayer']['level']
    #obj['allPlayers'][0]['scores']['kills']
    #obj['allPlayers'][0]['scores']['deaths']
    #obj['allPlayers'][0]['scores']['assists']
    #obj['allPlayers'][0]['scores']['creepScore'] # create also creep_score_per_min?
    return relevant_data
    #except Exception as e:
    #    print(e)


def calculate_insights(value, threshold_list: list(), description):

    assert len(threshold_list) == 3
    performance_str = str()
    if value < threshold_list[0]:
        if value < threshold_list[1]:
            performance_str = 'TERRIBLE {}'.format(description)
        else:
            performance_str = 'NOT SO GOOD {}'.format(description)
    else:
        if value > threshold_list[2]:
            performance_str = 'EXCELLENT {}'.format(description)
        else:
            performance_str = 'GOOD {}'.format(description)
    return performance_str
    




def predict(obj, predictor):
    assert type(obj) == type(dict())

    game_duration = obj['duration']
    del obj['duration']


    # build dataframe structure with current data
    df = pd.DataFrame.from_dict([obj]) # You may try wrapping your dictionary into a list:
    # https://stackoverflow.com/questions/17839973/constructing-pandas-dataframe-from-values-in-variables-gives-valueerror-if-usi
    
    df = TabularDataset(df)



    #print(df.head(1))   

    result = predictor.predict(df)

    current_performance = predictor.predict(df).iloc[0]
    status = str()
    if current_performance < 49.39:
        status = '[LOSE]'
        if current_performance < 33.95:
            status += '[HARD]'
    elif current_performance >= 49.39:
        status = '[WIN]'
        if current_performance > 65.10:
            status += '[HARD]'


    ''' taken from my dataset:

    calculated_player_performance	f1	f2	f3
    count	427984.000000	427984.000000	427984.000000	427984.000000
    mean	49.330796	0.200415	0.483173	0.514130
    std	22.320705	0.105837	0.244079	0.082497
    min	-111.160000	0.000000	0.000000	0.025222
    25%	33.950000	0.126134	0.306988	0.462111
    50%	49.390000	0.194691	0.466420	0.505454
    75%	65.100000	0.267318	0.639247	0.555198
    max	227.950000	1.209217	3.627652	4.508792
    '''

    # Also, extract detailed insights on f1, f2, f3
    threshold_f1 = [0.194691, 0.126134, 0.267318]
    threshold_f2 = [0.466420, 0.306988, 0.639247]
    threshold_f3 = [0.505454, 0.462111, 0.555198]

    f1_performance = str()
    f2_performance = str()
    f3_performance = str()

    print(obj)

    # Since f1 and f2 can have zero-values, we need to make sure we don't misinterpret this as having a terrible performance.
    if obj['f1'] == 0.0:
        f1_performance = 'NEED MORE DATA TO COMPUTE death ratio performance'
    else:
        f1_performance = calculate_insights(obj['f1'], threshold_f1, 'death ratio')

    if obj['f2'] == 0.0:
        f2_performance = 'NEED MORE DATA TO COMPUTE kills + assists performance'
    else:
        f2_performance = calculate_insights(obj['f2'], threshold_f2, 'kills + assists')
 
    if game_duration < 2:
        f3_performance = 'NEED MORE DATA TO COMPUTE XP performance'
    else:
        f3_performance = calculate_insights(obj['f3'], threshold_f3, 'xp')

    print('[{}][DR] {}'.format(datetime.datetime.now(), f1_performance))
    print('[{}][K/A] {}'.format(datetime.datetime.now(), f2_performance))
    print('[{}][XP] {}'.format(datetime.datetime.now(), f3_performance))

    status += ' by {}%'.format(abs(50 - current_performance))
    print('[{}] {}'.format(datetime.datetime.now(), status))

    # So, depending on these statistics, user will receive a feedback based on q1, q2, q3




# Load saved model from disk.
predictor = TabularPredictor.load(args.model_path, require_py_version_match=False)

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
        result = build_object(response.content)
        result = parse_object(result)
        predict(result, predictor)
    time.sleep(2) # wait 10 seconds before making another request