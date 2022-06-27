# Copyright (c) 2021 Oracle and/or its affiliates.

from oracledb import exceptions
from utils.oracle_database import OracleJSONDatabaseThinConnection, OracleJSONDatabaseThickConnection
import sys
from attr import Attribute
import requests
import yaml
import datetime
import pandas as pd
import time
import os
from pathlib import Path
import argparse
import ujson as json
home = str(Path.home())
p = os.path.abspath('..')
sys.path.insert(1, p)  # add parent directory to path.
# parse arguments for different execution modes.
parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mode', help='Mode to execute',
                    choices=['player_list', 'match_list', 'match_download_standard',
                             'match_download_detail', 'process_predictor', 'process_predictor_liveclient'],
                    required=False)
args = parser.parse_args()


def process_yaml():
    with open("../config.yaml") as file:
        return yaml.safe_load(file)


request_regions = ['br1', 'eun1', 'euw1', 'jp1',
                   'kr', 'la1', 'la2', 'na1', 'oc1', 'ru', 'tr1']


api_key = process_yaml()['riot_api_key']
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": api_key
}

# 1000 requests per minute using development key
# AK89OMWJzaal2SSLDtQszoKUZ220Akz0JppfTK6pF97VYve_KQEHcA9RdEx88ghXl_SbW6Nfpj2xyg


def get_puuid(request_ref, summoner_name, region, db):
    request_url = 'https://{}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}'.format(
        request_ref, summoner_name, region)  # europe, JASPERAN, EUW

    response = requests.get(request_url, headers=headers)
    time.sleep(1)
    if response.status_code == 200:
        #print('Printing response for user {} - region {}: -----\n{}'.format(summoner_name, region, response.json()))
        pass
    elif response.status_code == 404:
        print('PUUID not found for summoner {}'.format(summoner_name))
        db.delete('summoner', 'summonerName', summoner_name)
    else:
        print('Request error (@get_puuid). HTTP code {}'.format(response.status_code))
        return
    puuid = response.json().get('puuid')
    return puuid


# encrypted summoner ID: y8zda_vuZ5AkVYk8yXJrHa_ppKjIblOGKPCwzYcX9ywo4G0
# will return the PUUID but can be changed to return anything.
def get_summoner_information(summoner_name, request_region):
    assert request_region in request_regions

    request_url = 'https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}'.format(
        request_region, summoner_name)

    response = requests.get(request_url, headers=headers)
    if response.status_code != 200:
        print('Request error (@get_summoner_information). HTTP code {}'.format(response.status_code))
        return None
    return response.json().get('puuid')


def get_champion_mastery(encrypted_summoner_id, request_region):
    assert request_region in request_regions

    request_url = 'https://{}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{}'.format(
        request_region, encrypted_summoner_id)

    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        print('{}'.format(response.json()))
    else:
        print('Request error (@get_champion_mastery). HTTP code {}'.format(response.status_code))

    # Get champion IDs
    champion_df = pd.read_csv('../data/champion_ids.csv')

    # Example: get champion name by its id.
    #print(champion_df.loc[champion_df['champion_id'] == 103])
    # Processing of the information
    print('Total champions played: {}'.format(len(response.json())))
    for i in response.json():
        champion_name = champion_df.loc[champion_df['champion_id'] == i.get(
            'championId')]['champion_name'].to_string().split('    ')[1]  # get the champion name only
        print('Champion ID {} | Champion Name {} | Mastery level {} | Total mastery points {} | Last time played {} | Points until next mastery level {} | Chest granted {} | Tokens earned {}'.format(
            i.get('championId'),
            champion_name,
            i.get('championLevel'),
            i.get('championPoints'),
            datetime.datetime.fromtimestamp(
                i.get('lastPlayTime')/1000).strftime('%c'),
            i.get('championPointsUntilNextLevel'),
            i.get('chestGranted'),
            i.get('tokensEarned')))


def get_total_champion_mastery_score(encrypted_summoner_id, request_region):
    assert request_region in request_regions
    request_url = 'https://{}.api.riotgames.com/lol/champion-mastery/v4/scores/by-summoner/{}'.format(
        request_region, encrypted_summoner_id)

    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        print('{}'.format(response.json()))
    else:
        print('Request error (@get_total_champion_mastery_score). HTTP code {}'.format(response.status_code))


def get_user_leagues(encrypted_summoner_id, request_region):
    assert request_region in request_regions
    request_url = 'https://{}.api.riotgames.com/lol/league/v4/entries/by-summoner/{}'.format(
        request_region, encrypted_summoner_id)

    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        print('{}'.format(response.json()))
    else:
        print(
            'Request error (@get_user_leagues). HTTP code {}'.format(response.status_code))

    for i in response.json():
        if i.get('leaguePoints') != 100:
            print('Queue type: {} | Rank: {} {} {} LP | Winrate: {}% | Streak {} | >100 games {} | Inactive {}'.format(
                i.get('queueType'),
                i.get('tier'),
                i.get('rank'),
                i.get('leaguePoints'),
                (i.get('wins') / (i.get('losses') + i.get('wins'))) * 100,
                i.get('hotStreak'),
                i.get('veteran'),
                i.get('inactive')))
        else:
            print('Queue type: {} | Rank: {} {} {} LP - Promo standings: {}/{} | Winrate: {}% | Streak {} | >100 games {} | Inactive {}'.format(
                i.get('queueType'),
                i.get('tier'),
                i.get('rank'),
                i.get('leaguePoints'),
                i.get('miniSeries').get('wins'),
                i.get('miniSeries').get('losses'),
                (i.get('wins') / (i.get('losses') + i.get('wins'))) * 100,
                i.get('hotStreak'),
                i.get('veteran'),
                i.get('inactive')))


def get_n_match_ids(puuid, num_matches, queue_type, region):
    available_regions = ['europe', 'americas', 'asia']
    queue_types = ['ranked', 'tourney', 'normal', 'tutorial']
    assert region in available_regions
    assert queue_type in queue_types
    assert num_matches in range(0, 991)
    returning_object = list()
    iterator = 0
    request_url = 'https://{}.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?type={}&start={}&count={}'.format(
        region,
        puuid,
        queue_type,
        iterator,
        100
    )

    for x in range(int(num_matches / 100)):
        response = requests.get(request_url, headers=headers)
        time.sleep(1)
        if response.status_code != 200:
            print('Request error (@get_n_match_ids). HTTP code {}: {}'.format(
                response.status_code, response.json()))
        # Return the list of matches.
        for i in response.json():
            returning_object.append(
                {
                    'match_id': i
                }
            )
        # Modify the next request_url.
        iterator = iterator + 100
        request_url = 'https://{}.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?type={}&start={}&count={}'.format(
            region,
            puuid,
            queue_type,
            iterator,
            100
        )
    print('@get_n_match_ids: obtained {} matches from region {}'.format(len(returning_object), region))
    return returning_object


def get_match_timeline(match_id, region):
    available_regions = ['europe', 'americas', 'asia']
    assert region in available_regions
    request_url = 'https://{}.api.riotgames.com/lol/match/v5/matches/{}/timeline'.format(
        region,
        match_id
    )

    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        print('{}'.format(response.json()))
    else:
        print(
            'Request error (@get_match_timeline). HTTP code {}'.format(response.status_code))
        return None
    # Return the list of matches.
    return response.json()


def get_match_info(match_id, region):
    available_regions = ['europe', 'americas', 'asia']
    assert region in available_regions
    request_url = 'https://{}.api.riotgames.com/lol/match/v5/matches/{}'.format(
        region,
        match_id
    )

    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        print('{}'.format(response.json()))
    else:
        print('Request error (@get_match_info). HTTP code {}'.format(response.status_code))
    # Return the list of matches.
    return response.json()


# auxiliary function
def determine_overall_region(region):
    overall_region = str()
    tagline = str()
    if region in ['euw1', 'eun1', 'ru', 'tr1']:
        overall_region = 'europe'
    elif region in ['br1', 'la1', 'la2', 'na1']:
        overall_region = 'americas'
    else:
        overall_region = 'asia'
    # BR1, EUNE, EUW, JP1, KR, LA1, LA2, NA, OCE, RU, TR
    if region in ['br1', 'jp1', 'kr', 'la1', 'la2', 'ru', 'na1', 'tr1', 'oc1']:
        tagline = region.upper()
    elif region == 'euw1':
        tagline = 'EUW'
    elif region == 'eun1':
        tagline = 'EUNE'
    # 3 cases left: OCE
    return overall_region, tagline


def get_top_players(region, queue, db):
    assert region in request_regions
    assert queue in ['RANKED_SOLO_5x5', 'RANKED_FLEX_SR', 'RANKED_FLEX_TT']

    total_users_to_insert = list()
    # master, grandmaster and challenger endpoints

    request_urls = [
        'https://{}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/{}'.format(
            region,
            queue
        ),
        'https://{}.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/{}'.format(
            region,
            queue
        ),
        'https://{}.api.riotgames.com/lol/league/v4/masterleagues/by-queue/{}'.format(
            region,
            queue
        )
    ]

    for x in request_urls:
        response = requests.get(x, headers=headers)
        if response.status_code == 200:
            try:
                print('Region: {} | Tier: {} | Queue: {} | Total Players: {}'.format(region, response.json()['tier'],
                                                                                     response.json()['queue'], len(response.json()['entries'])))
            except KeyError:
                pass
            for y in response.json()['entries']:
                try:
                    y['tier'] = response.json()['tier']
                    y['request_region'] = region
                    y['queue'] = queue
                    total_users_to_insert.append(y)
                except KeyError:
                    pass
        else:
            print('Request error (@get_top_players). HTTP code {}: {}'.format(
                response.status_code, response.json()))

    print('Total users obtained in region {} and queue {}: {}'.format(
        region, queue, len(total_users_to_insert)))

    # Insert into the database.
    collection_summoner = db.get_connection(
    ).getSodaDatabase().createCollection('summoner')

    # Insert the users.
    for x in total_users_to_insert:
        x['request_region'] = region
        x['queue'] = queue
        try:
            qbe = {'summonerId': x['summonerId']}
            if len(collection_summoner.find().filter(qbe).getDocuments()) == 0:
                # In case they don't exist in the DB, we get their PUUIDs, in case they change their name.
                overall_region, tagline = determine_overall_region(region)
                x['puuid'] = get_puuid(
                    overall_region, x['summonerName'], tagline, db)
                db.insert('summoner', x)
                print('Inserted new summoner: {} in region {}, queue {}'.format(
                    x['summonerName'], region, queue))
            else:
                print('Summoner {} already inserted'.format(x['summonerName']))
                continue
        except exceptions.IntegrityError:
            print('Summoner {} already inserted'.format(x['summonerName']))
            continue


# this function helps modify a column value
def change_column_value_by_key(db, collection_name, column_name, column_value, key):
    connection = db.get_connection()
    collection = connection.getSodaDatabase().createCollection(
        collection_name)  # get collection
    found_doc = collection.find().key(key).getOne()  # find document by key
    content = found_doc.getContent()
    # change value of column_name to column_value
    content[column_name] = column_value
    collection.find().key(key).replaceOne(content)  # replace document
    print('[DBG] UPDATE BIT {}: {}'.format(column_name,
          collection.find().key(key).getOne().getContent()[column_name]))
    db.close_connection(connection)


def extract_matches(region, match_id, db, key):
    available_regions = ['europe', 'americas', 'asia']
    assert region in available_regions
    request_url = 'https://{}.api.riotgames.com/lol/match/v5/matches/{}'.format(
        region,
        match_id
    )

    response = requests.get(request_url, headers=headers)
    time.sleep(1.5)  # rate limiting purposes
    if response.status_code != 200:
        print('Request error (@extract_matches). HTTP code {}'.format(response.status_code))
        return
    # Get participants and teams.objectives objects
    o_version = response.json().get('info').get('gameVersion')
    o_participants = response.json().get('info').get('participants')
    o_teams = response.json().get('info').get('teams')

    matchups = {
        'top': list(),
        'middle': list(),
        'bottom': list(),
        'utility': list(),
        'jungle': list()
    }
    # Extract individual matchups
    for x in o_participants:
        try:
            matchups['{}'.format(x.get('individualPosition').lower())].append(
                {
                    'champion': x.get('championName'),
                    'assists': x.get('assists'),
                    'deaths': x.get('deaths'),
                    'goldEarned': x.get('goldEarned'),
                    'kills': x.get('kills'),
                    'puuid': x.get('puuid'),
                    'summonerName': x.get('summonerName'),
                    'totalDamageDealtToChampions': x.get('totalDamageDealtToChampions'),
                    'totalMinionsKilled': x.get('totalMinionsKilled'),
                    'visionScore': x.get('visionScore'),
                    'win': x.get('win')
                }
            )
        except KeyError:
            # Then we have an Invalid position detected (probably AFK). In this case, we ignore it.
            continue
    # Check lengths to see if any lanes had invalid matchups. In this case, remove them.
    for x, y in matchups.items():
        if len(y) != 2:
            #print('[ERR] Detected error in {} lane'.format(x))
            continue
        else:
            # We insert our matchups info into the db
            # First check which of these are not present.
            match_id = response.json().get('metadata').get('matchId')
            to_insert_obj = {
                'p_match_id': '{}_{}'.format(match_id, x),
                'data': y,
                'gameVersion': o_version
            }
            try:
                db.insert('matchups', to_insert_obj)
            except exceptions.IntegrityError:
                print('Match details {} already inserted'.format(
                    to_insert_obj.get('p_match_id')))
                continue
            print('Inserted new matchup with ID {} in region {}'.format(
                '{}_{}'.format(match_id, x), region))

    # Now, set a processed_1v1 bit in the match
    change_column_value_by_key(db, 'match', 'processed_1v1', 1, key)

    return response.json()


def player_list(db):
    # Get top players from API and add them to our DB.
    for x in request_regions:
        # RANKED_FLEX_TT disabled since the map was removed
        for y in ['RANKED_SOLO_5x5', 'RANKED_FLEX_SR']:
            get_top_players(x, y, db)


def match_list(db):
    # From all users in the collection, extract matches
    all_match_ids = list()
    soda = db.get_connection().getSodaDatabase()
    collection_summoner = soda.createCollection('summoner')
    collection_match = soda.createCollection('match')

    all_summoners = collection_summoner.find().getDocuments()

    for x in all_summoners:
        current_summoner = x.getContent()
        current_summoner_puuid = get_summoner_information(
            current_summoner['summonerName'], current_summoner['request_region'])
        if current_summoner_puuid is None:
            continue
        for y in ['europe', 'americas', 'asia']:
            for z in ['ranked', 'tourney']:
                z_match_ids = get_n_match_ids(
                    current_summoner_puuid, 990, z, y)
                # Insert them into our match collection
                for i in z_match_ids:
                    try:
                        collection_match.insertOne(i)
                    except exceptions.IntegrityError:
                        print('Match ID {} already inserted'.format(i))
                        continue
                    print('Inserted new match with ID {} from summoner {} in region {}, queue {}'.format(i['match_id'],
                                                                                                         current_summoner['summonerName'], y, z))


def match_download_standard(db):
    # We have the match IDs, let's get some info about the games.
    collection_match = db.get_connection().getSodaDatabase().createCollection('match')
    all_match_ids = collection_match.find().filter(
        {'processed_1v1': {"$ne": 1}}).getDocuments()
    for x in all_match_ids:
        # Get the overall region to make the proper request
        overall_region, tagline = determine_overall_region(
            x.getContent().get('match_id').split('_')[0].lower())
        print('Overall Region {} detected'.format(overall_region))
        extract_matches(overall_region, x.getContent().get(
            'match_id'), db, x.key)


def match_download_detail(db):
    collection_match = db.get_connection().getSodaDatabase().createCollection('match')
    all_match_ids = collection_match.find().filter(
        {'processed_5v5': {"$ne": 1}}).getDocuments()
    for x in all_match_ids:
        # Get the overall region to make the proper request
        overall_region, tagline = determine_overall_region(
            x.getContent().get('match_id').split('_')[0].lower())
        print('Overall Region {} detected'.format(overall_region))
        match_detail = get_match_timeline(
            x.getContent().get('match_id'), overall_region)
        if match_detail:
            db.insert('match_detail', match_detail)
            # Now, set a processed_5v5 bit in the match in order not to process it again in the future.
            change_column_value_by_key(db, 'match', 'processed_5v5', 1, x.key)


def build_final_object(json_object):

    all_frames = list()

    try:
        match_id = json_object.get('metadata').get('matchId')
    except AttributeError:
        print('[DBG] ERR MATCH_ID RETRIEVAL: {}'.format(json_object))
        return

    winner = int()
    # Determine winner
    frames = json_object.get('info').get('frames')
    last_frame = frames[-1]
    last_event = last_frame.get('events')[-1]
    assert last_event.get('type') == 'GAME_END'
    winner = last_event.get('winningTeam')

    for x in json_object.get('info').get('frames'):

        for y in range(1, 11):
            frame = {
                "timestamp": x.get('timestamp')
            }
            frame['abilityPower'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('abilityPower')
            frame['armor'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('armor')
            frame['armorPen'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('armorPen')
            frame['armorPenPercent'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('armorPenPercent')
            frame['attackDamage'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('attackDamage')
            frame['attackSpeed'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('attackSpeed')
            frame['bonusArmorPenPercent'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('bonusArmorPenPercent')
            frame['bonusMagicPenPercent'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('bonusMagicPenPercent')
            frame['ccReduction'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('ccReduction')
            frame['cooldownReduction'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('cooldownReduction')
            frame['health'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('health')
            frame['healthMax'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('healthMax')
            frame['healthRegen'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('healthRegen')
            frame['lifesteal'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('lifesteal')
            frame['magicPen'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('magicPen')
            frame['magicPenPercent'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('magicPenPercent')
            frame['magicResist'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('magicResist')
            frame['movementSpeed'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('movementSpeed')
            frame['power'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('power')
            frame['powerMax'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('powerMax')
            frame['powerRegen'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('powerRegen')
            frame['spellVamp'] = x.get('participantFrames').get(
                '{}'.format(y)).get('championStats').get('spellVamp')
            frame['magicDamageDone'] = x.get('participantFrames').get(
                '{}'.format(y)).get('damageStats').get('magicDamageDone')
            frame['magicDamageDoneToChampions'] = x.get('participantFrames').get(
                '{}'.format(y)).get('damageStats').get('magicDamageDoneToChampions')
            frame['magicDamageTaken'] = x.get('participantFrames').get(
                '{}'.format(y)).get('damageStats').get('magicDamageTaken')
            frame['physicalDamageDone'] = x.get('participantFrames').get(
                '{}'.format(y)).get('damageStats').get('physicalDamageDone')
            frame['physicalDamageDoneToChampions'] = x.get('participantFrames').get(
                '{}'.format(y)).get('damageStats').get('physicalDamageDoneToChampions')
            frame['physicalDamageTaken'] = x.get('participantFrames').get(
                '{}'.format(y)).get('damageStats').get('physicalDamageTaken')
            frame['totalDamageDone'] = x.get('participantFrames').get(
                '{}'.format(y)).get('damageStats').get('totalDamageDone')
            frame['totalDamageDoneToChampions'] = x.get('participantFrames').get(
                '{}'.format(y)).get('damageStats').get('totalDamageDoneToChampions')
            frame['totalDamageTaken'] = x.get('participantFrames').get(
                '{}'.format(y)).get('damageStats').get('totalDamageTaken')
            frame['trueDamageDone'] = x.get('participantFrames').get(
                '{}'.format(y)).get('damageStats').get('trueDamageDone')
            frame['trueDamageDoneToChampions'] = x.get('participantFrames').get(
                '{}'.format(y)).get('damageStats').get('trueDamageDoneToChampions')
            frame['trueDamageTaken'] = x.get('participantFrames').get(
                '{}'.format(y)).get('damageStats').get('trueDamageTaken')

            frame['goldPerSecond'] = x.get('participantFrames').get(
                '{}'.format(y)).get('jungleMinionsKilled')
            frame['jungleMinionsKilled'] = x.get('participantFrames').get(
                '{}'.format(y)).get('jungleMinionsKilled')
            frame['level'] = x.get('participantFrames').get(
                '{}'.format(y)).get('level')
            frame['minionsKilled'] = x.get('participantFrames').get(
                '{}'.format(y)).get('minionsKilled')
            frame['participantId'] = x.get('participantFrames').get(
                '{}'.format(y)).get('participantId')
            frame['timeEnemySpentControlled'] = x.get('participantFrames').get(
                '{}'.format(y)).get('timeEnemySpentControlled')
            frame['totalGold'] = x.get('participantFrames').get(
                '{}'.format(y)).get('totalGold')
            frame['xp'] = x.get('participantFrames').get(
                '{}'.format(y)).get('xp')

            frame['identifier'] = '{}_{}'.format(
                match_id, frame['participantId'])

            if winner == 100:
                if y in (1, 2, 3, 4, 5):
                    frame['winner'] = 1
                else:
                    frame['winner'] = 0
            elif winner == 200:
                if y in (1, 2, 3, 4, 5):
                    frame['winner'] = 0
                else:
                    frame['winner'] = 1
            all_frames.append(frame)
            del frame

    return all_frames


# builds liveclient-affine data object.
def build_final_object_liveclient(json_object):
    all_frames = list()
    match_id = str()
    try:
        match_id = json_object.get('metadata').get('matchId')
    except AttributeError:
        print('[DBG] ERR MATCH_ID RETRIEVAL: {}'.format(json_object))
        return

    winner = int()
    # Determine winner
    frames = json_object.get('info').get('frames')
    last_frame = frames[-1]
    last_event = last_frame.get('events')[-1]
    assert last_event.get('type') == 'GAME_END'
    winner = last_event.get('winningTeam')

    for x in json_object.get('info').get('frames'):

        for y in range(1, 11):
            frame = {
                'timestamp': x.get('timestamp')
            }
            try:
                frame['abilityPower'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('abilityPower')
                frame['armor'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('armor')
                frame['armorPenetrationFlat'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('armorPen')
                frame['armorPenetrationPercent'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('armorPenPercent')
                frame['attackDamage'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('attackDamage')
                frame['attackSpeed'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('attackSpeed')
                frame['bonusArmorPenetrationPercent'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('bonusArmorPenPercent')
                frame['bonusMagicPenetrationPercent'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('bonusMagicPenPercent')
                frame['cooldownReduction'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('cooldownReduction')
                frame['currentHealth'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('health')
                frame['maxHealth'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('healthMax')
                frame['healthRegenRate'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('healthRegen')
                frame['lifesteal'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('lifesteal')
                frame['magicPenetrationFlat'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('magicPen')
                frame['magicPenetrationPercent'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('magicPenPercent')
                frame['magicResist'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('magicResist')
                frame['moveSpeed'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('movementSpeed')
                frame['resourceValue'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('power')
                frame['resourceMax'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('powerMax')
                frame['resourceRegenRate'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('powerRegen')
                frame['spellVamp'] = x.get('participantFrames').get(
                    '{}'.format(y)).get('championStats').get('spellVamp')
                frame['identifier'] = '{}_{}'.format(match_id, x.get(
                    'participantFrames').get('{}'.format(y)).get('participantId'))
            except AttributeError as e:
                print('[DBG] LIVECLIENT BUILDING OBJECT FAILED: {}'.format(e))
                # if there's a problem with a frame, skip this iteration
                return list()

            if winner == 100:
                if y in (1, 2, 3, 4, 5):
                    frame['winner'] = 1
                else:
                    frame['winner'] = 0
            elif winner == 200:
                if y in (1, 2, 3, 4, 5):
                    frame['winner'] = 0
                else:
                    frame['winner'] = 1
            all_frames.append(frame)
            del frame

    return all_frames


# ------------------
# CLASSIFIER MODEL (NO LIVE CLIENT API STRUCTURE)
def process_predictor(db):
    connection = db.get_connection()
    matches = connection.getSodaDatabase().createCollection('match_detail')
    # Total documents left to process:
    print('Total match_detail documents (to process): {}'.format(
        matches.find().filter({'classifier_processed': {"$ne": 1}}).count()))

    for doc in matches.find().filter({'classifier_processed': {"$ne": 1}}).getCursor():
        content = doc.getContent()
        built_object = build_final_object(content)
        if built_object:
            for x in built_object:
                res = db.insert('predictor', x)  # insert in new collection.
                if res == -1:
                    # Change column value to processed.
                    print(doc.getContent().get('metadata').get('matchId'))
                    # after processing, update processed bit.
                    change_column_value_by_key(
                        db, 'match_detail', 'classifier_processed', 1, doc.key)
                    break
    db.close_connection(connection)


# CLASSIFIER MODEL (LIVE CLIENT API AFFINITY DATA)
def process_predictor_liveclient(db):
    connection = db.get_connection()
    matches = connection.getSodaDatabase().createCollection('match_detail')
    print('Total match_detail documents (to process): {}'.format(
        matches.find().filter({'classifier_processed_liveclient': {"$ne": 1}}).count()))

    for doc in matches.find().filter({'classifier_processed_liveclient': {"$ne": 1}}).getCursor():
        content = doc.getContent()
        # build data similar to the one given by the Live Client API from Riot.
        built_object = build_final_object_liveclient(content)
        if built_object:
            for x in built_object:
                # insert in new collection.
                res = db.insert('predictor_liveclient', x)
                if res == -1:
                    # Change column value to processed.
                    print(doc.getContent().get('metadata').get('matchId'))
                    # after processing, update processed bit.
                    change_column_value_by_key(
                        db, 'match_detail', 'classifier_processed_liveclient', 1, doc.key)
                    break
    db.close_connection(connection)


# TODO
def process_regressor(db):
    pass


# TODO
def process_regressor_liveclient(db):
    pass


def data_mine(db):
    if args.mode == 'player_list':
        player_list(db)
    elif args.mode == 'match_list':
        match_list(db)
    elif args.mode == 'match_download_standard':
        match_download_standard(db)
    elif args.mode == 'match_download_detail':
        match_download_detail(db)
    elif args.mode == 'process_predictor':
        process_predictor(db)
    elif args.mode == 'process_predictor_liveclient':
        process_predictor_liveclient(db)
    elif args.mode == 'process_regressor':
        process_regressor(db)
    elif args.mode == 'process_regressor_liveclient':
        process_regressor_liveclient(db)
    else:  # we execute everything.
        player_list(db)
        match_list(db)
        match_download_standard(db)
        match_download_detail(db)


def main():
    db = OracleJSONDatabaseThickConnection()
    data_mine(db)
    db.close_pool()


if __name__ == '__main__':
    main()
