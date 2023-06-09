from utils.oracle_database import OracleJSONDatabaseThickConnection
import sys
from attr import Attribute
import requests
import datetime
import pandas as pd
import time
from pathlib import Path
import argparse
import ujson as json
import time

load_dotenv()

riot_api_key = os.getenv("RIOT_API_KEY")


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
        print('{} Request error (@extract_matches). HTTP code {}'.format(time.strftime("%Y-%m-%d %H:%M"), response.status_code))
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
                print('{} Match details {} already inserted'.format(
                    time.strftime("%Y-%m-%d %H:%M"),
                    to_insert_obj.get('p_match_id')))
                continue
            print('{} Inserted new matchup with ID {} in region {}'.format(
                time.strftime("%Y-%m-%d %H:%M"),
                '{}_{}'.format(match_id, x), region))

    # Now, set a processed_1v1 bit in the match
    change_column_value_by_key(db, 'match', 'processed_1v1', 1, key)

    return response.json()


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



def match_download_standard(db):
    # We have the match IDs, let's get some info about the games.
    collection_match = db.get_connection().getSodaDatabase().createCollection('match')
    all_match_ids = collection_match.find().filter(
        {'processed_1v1': {"$ne": 1}}).getDocuments()
    for x in all_match_ids:
        # Get the overall region to make the proper request
        overall_region, tagline = determine_overall_region(
            x.getContent().get('match_id').split('_')[0].lower())
        print('{} Overall Region {} detected'.format(time.strftime("%Y-%m-%d %H:%M"), overall_region))
        extract_matches(overall_region, x.getContent().get(
            'match_id'), db, x.key)


def data_mine(db):
        match_download_standard(db)


def main():
    db = OracleJSONDatabaseThickConnection()
    data_mine(db)
    db.close_pool()