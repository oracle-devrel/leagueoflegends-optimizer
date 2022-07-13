'''
@author jasperan

This is a very lightweight version of the original file (league.py) to test out the functionality
of the Riot Games API.

Only two options are available: player_list and match_list. To get all available functionality use league.py
'''

# Copyright (c) 2021 Oracle and/or its affiliates.

import requests
import yaml
import datetime
import pandas as pd
import time
import os
from pathlib import Path
import argparse
import ujson as json
# parse arguments for different execution modes.
parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mode', help='Mode to execute',
                    choices=['player_list', 'match_list'],
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


def get_puuid(request_ref, summoner_name, region):
    request_url = 'https://{}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}'.format(
        request_ref, summoner_name, region)  # europe, JASPERAN, EUW

    response = requests.get(request_url, headers=headers)
    time.sleep(1)
    if response.status_code == 200:
        #print('Printing response for user {} - region {}: -----\n{}'.format(summoner_name, region, response.json()))
        pass
    elif response.status_code == 404:
        print('PUUID not found for summoner {}'.format(summoner_name))
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


def get_total_champion_mastery_score(encrypted_summoner_id, request_region):
    assert request_region in request_regions
    request_url = 'https://{}.api.riotgames.com/lol/champion-mastery/v4/scores/by-summoner/{}'.format(
        request_region, encrypted_summoner_id)

    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        print('{}'.format(response.json()))
    else:
        print('Request error (@get_total_champion_mastery_score). HTTP code {}'.format(response.status_code))


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


def get_top_players(region, queue):
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

    # Insert the users.
    for x in total_users_to_insert:
        x['request_region'] = region
        x['queue'] = queue
        # In case they don't exist in the DB, we get their PUUIDs, in case they change their name.
        overall_region, tagline = determine_overall_region(region)
        x['puuid'] = get_puuid(overall_region, x['summonerName'], tagline)
        print('Obtained new summoner: {} in region {}, queue {}'.format(
            x['summonerName'], region, queue))

    return total_users_to_insert


def extract_matches(region, match_id, key):
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
    for x, y in matchups.items():
        if len(y) != 2:
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
            except cx_Oracle.IntegrityError:
                print('Match details {} already inserted'.format(
                    to_insert_obj.get('p_match_id')))
                continue
            print('Inserted new matchup with ID {} in region {}'.format(
                '{}_{}'.format(match_id, x), region))

    return response.json()


def player_list():
    # Get top players from API and add them to our DB.
    for x in request_regions:
        # RANKED_FLEX_TT disabled since the map was removed
        for y in ['RANKED_SOLO_5x5', 'RANKED_FLEX_SR']:
            get_top_players(x, y)


def match_list(players):
    # From all users in the collection, extract matches
    all_match_ids = list()

    for x in players:
        current_summoner_puuid = get_summoner_information(
            x['summonerName'], x['request_region'])
        if current_summoner_puuid is None:
            continue
        for y in ['europe', 'americas', 'asia']:
            for z in ['ranked', 'tourney']:
                z_match_ids = get_n_match_ids(
                    current_summoner_puuid, 990, z, y)
                # Insert them into our match collection
                for i in z_match_ids:
                    print('Obtained new match with ID {} from summoner {} in region {}, queue {}'.format(i['match_id'],
                                                                                                         x['summonerName'], y, z))


def data_mine():
    if args.mode == 'player_list':
        player_list()
    elif args.mode == 'match_list':
        match_list()
    else:  # we execute everything.
        players = player_list()
        match_list(players)


def main():
    data_mine()


if __name__ == '__main__':
    main()
