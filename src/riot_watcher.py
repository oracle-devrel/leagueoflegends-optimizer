from riotwatcher import LolWatcher, ApiError
from rich import print
import ujson as json
import argparse
import os.path
import requests
from requests.exceptions import HTTPError
# parse arguments for different execution modes.
parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', help='Verbose mode',
    required=False, default=False)
parser.add_argument('-u', '--username', help='Player username',
    required=True)

args = parser.parse_args()


#'''
#players_to_analyze = ['Licorice', 'bwipobwipobwipo', '서쪽에서 최고', 
#                      'River9', 'bai ri meng', 'la ji game', 'Icelandboy', 'Icelandwinter',
#                      'Stixxay', 'IPlayYouListen',
#                      'haru dad', '70ping gamer huhi']
#''' # all NA, EU and KR accounts
# trying only with NA accounts first:
players_to_analyze = list()

# gsw case
if args.username != 'gsw':
   players_to_analyze = [args.username]
else:
    print('##### GSW MODE #####')
    players_to_analyze = ['Licorice', 'Stixxay', 'haru dad', 'IPlayYouListen', '70ping gamer huhi']
    print('##### PLAYERS TO ANALYZE {}'.format(players_to_analyze))

                      
lol_watcher = LolWatcher('xxxxxxxxxxxxxxxxxxxxxx')

my_region = 'na1'

for player in players_to_analyze:
    try:
        me = lol_watcher.summoner.by_name(my_region, player)
    except ApiError as err:
        if err.response.status_code == 404:
            print('Summoner with that summoner name not found.')
        continue
    print(me) if args.verbose else None


    # all objects are returned (by default) as a dict
    my_ranked_stats = lol_watcher.league.by_summoner(my_region, me['id'])
    print(my_ranked_stats) if args.verbose else None


    '''
    # First we get the latest version of the game from data dragon
    versions = lol_watcher.data_dragon.versions_for_region(my_region)
    champions_version = versions['n']['champion']
    '''

    matches = lol_watcher.match.matchlist_by_puuid(my_region, me['puuid'], count=100)
    print(matches) if args.verbose else None


    '''
    # Get a player's total champion mastery score, which is the sum of individual champion mastery levels
    champion_scores = lol_watcher.champion_mastery.scores_by_summoner(my_region, me['id'])
    print(champion_scores)
    '''

    max = len(matches)
    i = 0
    for x in matches:
        file_names = ['data/{}_{}.txt'.format(player, x), 'data/{}_{}_timeline.txt'.format(player, x)]
        if os.path.isfile(file_names[0]):
            # skip this iteration as we have already processed this call.
            print('[DUPLICATE] Skipping {}'.format(x))
            i += 1
            continue

        # otherwise, download the match and timeline.
        try:
            match_info = lol_watcher.match.by_id(my_region, x)
            match_timeline = lol_watcher.match.timeline_by_match(my_region, x)
        except HTTPError:
            print('[NOT FOUND] Could not find match {}. Skipping...'.format(x))
            i += 1
            continue

        print(match_info) if args.verbose else None
        print('Match timeline: {}'.format(match_timeline)) if args.verbose else None
        match_data = {
            'id': x,
            'data': match_info
        }
        timeline_data = {
            'id': x,
            'data': match_timeline
        }
        with open(file_names[0], 'w') as file:
            file.write(json.dumps(match_data))

        with open(file_names[1], 'w') as file:
            file.write(json.dumps(timeline_data))

        print('[{}] {}/{}'.format(player, i, max))
        i += 1




    # Lets get some champions
    #current_champ_list = lol_watcher.data_dragon.champions(champions_version)
    #print(current_champ_list)







    '''
    # For Riot's API, the 404 status code indicates that the requested data wasn't found and
    # should be expected to occur in normal operation, as in the case of a an
    # invalid summoner name, match ID, etc.
    #
    # The 429 status code indicates that the user has sent too many requests
    # in a given amount of time ("rate limiting").

    try:
        response = lol_watcher.summoner.by_name(my_region, 'this_is_probably_not_anyones_summoner_name')
    except ApiError as err:
        if err.response.status_code == 429:
            print('We should retry in {} seconds.'.format(err.response.headers['Retry-After']))
            print('this retry-after is handled by default by the RiotWatcher library')
            print('future requests wait until the retry-after time passes')
        elif err.response.status_code == 404:
            print('Summoner with that ridiculous name not found.')
        else:
            raise
    '''