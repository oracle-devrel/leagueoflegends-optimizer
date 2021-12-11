# League of Legends Optimizer using Oracle Cloud Infrastructure: Data Extraction & Processing

## Recap & Introduction
Welcome to the second article on the League of Legends Optimizer article series! In this article, we're going to continue where we left off in article one, Data Extraction and Processing. As a reminder, let's review what we covered last time last time:
- We defined and modelled our problem, understanding the different steps in the drafting phase of the game
- We explored the various endpoints offered by Riot Games in their official API
- We pulled data from the most skilled players around the world and built a data set of these players, which left us with a structure like this in our non-relational autonomous database:

```json
{
    "tier": "CHALLENGER",
    "veteran": false,
    "wins": 229,
    "request_region": "br1",
    "rank": "I",
    "inactive": false,
    "summonerId": "dKMYAJhqPpBuI9hSfIon_a4zSbtCwTFep-DA6Lq9YwqlIQ",
    "hotStreak": true,
    "queue": "RANKED_SOLO_5x5",
    "losses": 198,
    "freshBlood": true,
    "puuid": "aRjqIYDtBMBU2j-8EfHY6dJ0RZ9TqXgWLeNvpcjRWlCBaP8HGBAWFRAiehRM4Jo-lgJXXrjTCOcIKg",
    "summonerName": "Qats",
    "leaguePoints": 922
}
```

- We periodically extracted as many games as possible for each player, storing the Match ID’s in a specific collection in our database for further processing.

## Code Optimization

Before diving into building a dataset with match information, there are some things to consider:
1. The player and match datasets are ever-growing and will continue to expand in size and complexity if we keep executing our code
2. The functions __get_top_player()__ and __get_puuid()__ can be more thoroughly optimized

For that, I propose a code revamp and bugfix before resuming the ML pipeline work. It is important to keep optimizing code even when we think it will not matter, because in the end we might need to do it anyway. It's much better to have the ideas fresh rather than waiting for the right moment to do these optimizations and forgetting how to optimize the code at all.

### Optimizing API call efficiency
Our constantly-growing dataset made me realize there must be a way to retrieve skilled players without constantly requesting their PUUIDs. In fact, we should only retrieve the PUUID for a player if this player isn't already present in the database. By definition, the PUUID will never change even when summoners change their display / in-game names. The first order of optimization is to check whether players are already in our DB collection before requesting their PUUID. This will save us precious API calls which will allow our program to focus on processing, and less on API restrictions and rate limits.

```python
# Insert the users.
	for x in total_users_to_insert:
		x['request_region'] = region
		x['queue'] = queue
		try:
			qbe = {'summonerId':x['summonerId']}
			if len(collection_summoner.find().filter(qbe).getDocuments()) == 0:
				# In case they don't exist in the DB, we get their PUUIDs, in case they change their name.
				overall_region, tagline = determine_overall_region(region)
				x['puuid'] = get_puuid(overall_region, x['summonerName'], tagline, connection)
				collection_summoner.insertOne(x)
				print('Inserted new summoner: {} in region {}, queue {}'.format(x['summonerName'], region, queue))
			else:
				print('Summoner {} already inserted'.format(x['summonerName']))
				continue
		except cx_Oracle.IntegrityError:
			print('Summoner {} already inserted'.format(x['summonerName']))
			continue
```
As shown, we will check for new players in our collection before inserting them. In case they are not present, we'll request their PUUIDs and their respective information, and proceed to insert them.


Additionally, I also implemented a SODA database method that will remove faulty summoners (see __delete_json_db()__). In case a summoner can't be found given a specific username for a region, we will remove it from our DB since all subsequent requests (asking the Riot Games API for their games) will always result in errors:

```python
# Remove a document from a collection based on the key and value pairs provided.
def delete_json_db(connection, collection_name, on_column, on_value):
	soda = connection.getSodaDatabase()
	x_collection = soda.createCollection(collection_name)

	qbe = {on_column: on_value}
	x_collection.find().filter(qbe).remove()
```

When calling __get_puuid()__, we will check for the HTTPs response status code before doing anything:

```python
# Inside get_puuid()
if response.status_code == 200:
		#print('Printing response for user {} - region {}: -----\n{}'.format(summoner_name, region, response.json()))
		pass
	elif response.status_code == 404:
		print('PUUID not found for summoner {}'.format(summoner_name))
		delete_json_db(connection, 'summoner', 'summonerName', summoner_name)
	else:
		print('Request error (@get_puuid). HTTP code {}'.format(response.status_code))
		return
```

These two modifications may seem insignificant, but they improved the code efficiency by up to 80%, depending on the number of already-existing players in the **summoner** collection. Querying the API for new summoners was much faster, since duplicate values would be automatically ignored, and I'd only have to wait for the new ones' PUUIDs.

### Reducing Redundant Processing

Finally, as our last optimization, we will add new keys in our document, called **processed_1v1** and **processed_5v5**, which will indicate whether a match has already been processed for the 1v1 and 5v5 models or not (more on this in the next sections). In case this match has been processed, we will keep it in our dataset, but we will not extract the contents of the match from now on. This will reduce overloading the CPU and processing times of our Python code, since this data mining process has been programmed to take into consideration all values present in the database (as any data mining process should). 

Considering this previous collection structure:

```json
{
    "match_id": "BR1_2133968346"
}
```

We'll expand this into (example with a non-processed match):

```json
{
    "match_id": "BR1_2133968346",
    "processed_1v1": 0,
    "processed_5v5": 0
}
```

Subsequently, in our __data_mine()__ function, we will only process those matches who haven't been processed, and after processing, we will change their processed bit in order not to make redundant processing and API calls:

```python
all_match_ids = collection_match.find().filter({'processed_1v1': {"$ne":1}}).getDocuments()
```
After processing our 1v1 models, in the upcoming articles we will make the same filtering but for the other processed bit:
```python
all_match_ids = collection_match.find().filter({'processed_5v5': {"$ne":1}}).getDocuments()
```

## Extracting Game Data

Since we have a great collection of games, and our code has already __survived__ a code optimization iteration, we'll get straight into the data provided by Riot's API about matches. 

The preliminary structure of data that we can process is too large to paste here, but there's more than enough information. The following JSON structure outlines the most important variables that we might need.

```json
{
    "metadata": {
        "dataVersion": "2",
        "matchId": "BR1_2133968346",
        "participants": [
            "MAwy3tdjisAuet11VKKSM-WhzljY1onACC9rLpriEoWoAKGB8rNampDsoUy-1KBfYDCEAJcMqO33MQ",
            "zs2vbZ7MtlgtuSY1HaLPytK5mr07nGUXkXXQhPxIJ2uff07VNaRKJk_f-uxkDEIJGRf9Weg9y4bm3w",
            "GI68lPlGrXbLIZ_o536EFmf1FyWY9mjqEmeEeg6NHiKcUboLZpsKaXL5TvCa1aBBWQgE4c6Y2EzMbQ",
            "RznuEthBrn_aO6q4RWYwX-bp96BBcVVSccBsMUxRGMJsSrSiVR5cwpgqqpAE0krz5MzqGFbNVdtxXA",
            "x73jcQmLJozEJETZWF17Xz-8tqS7zUyT4vY2ctcYkz9vGmbM5sgNkPJmJE8U9W-9DSRce43cUn1yvg",
            "KbDKfIXKhdXrzDKyFdmSpLFfIHIiOYHIVqr0TFpHY4xIaoUUIH8nd0IgZV5C1E28c2vRLYLdU6uwRQ",
            "bEXzoqxnVFYL2-NwyHvv-u3x_ojRc_P-cf0INO8J_l_MVljXW-dA5xcXgBWnWmpFvG1YIMAFKDJcXg",
            "iV-M2lcWZ7cqLKKC4rrDy6TLx_W2QUIGRuqSyYzjW0zj8Ku6pwncIZctSqjFlUdpUErT7dB3muiuxQ",
            "PpcjIHRykKFBBiCVsx0f1YMnbQAL6It8TtBkORMFBuScePoB3s8pYX-kPZpgkmD0HVW65lFm7N3kGg",
            "p7GibwRhHT1jmmw7vXSVVSck2FDjBnxm_MyVlSL8Tko58qPHH9gy6wEwthuPbf98Zrn1J9qDhX4nPw"
        ]
    },
    "info": {
        "gameDuration": 1739425,
        "gameId": 2133968346,
        "gameVersion": "10.25.348.1797",
        "participants": ["a lot of information on individual scores, summoners, etc. From here we will just extract the championName for each player"],
        "platformId": "BR1",
        "teams": [
            {
                "bans": [
                    {
                        "championId": 25,
                        "pickTurn": 1
                    },
                    {
                        "championId": 121,
                        "pickTurn": 2
                    },
                    {
                    	"this goes on for all pick turns": 1
                    }
                ],
                "objectives": {
                    "baron": {
                        "first": false,
                        "kills": 1
                    },
                    "champion": {
                        "first": false,
                        "kills": 31
                    },
                    "dragon": {
                        "first": false,
                        "kills": 0
                    },
                    "inhibitor": {
                        "first": false,
                        "kills": 0
                    },
                    "riftHerald": {
                        "first": true,
                        "kills": 1
                    },
                    "tower": {
                        "first": true,
                        "kills": 2
                    }
                },
                "teamId": 100,
                "win": false
            },
            {"the same for the other team": 1}
        ]
    }
}
```
Note that the __championId__ variable is represented by a number. In case you want to make some additional processing and extract this information, [I have developed a Python script](../src/aux_files/process_data_dragon.py) which uses the official Riot Games' Data Dragon, which allows us to determine which champion ID corresponds to which champion name. 

From this amount of data, which is a lot, and according to the problem statement we discussed in [Article One](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/main/articles/article1.md), we need at least the following information:

- Patch number, since team compositions, and some aspects of the game change every patch due to changes in champions' stats
- Team 1 composition
- Team 2 composition
- Win Team 1 / Win Team 2 binary variable
- Whether each team did First Blood, First Dragon, Baron, Tower, Herald and Inhibitor. These are variables we would like to consider for more complex models, and we might do that.


## Modelling the Matchup Predictor

To create our first predictor and to test out the different possibilities of our models, we will build a structure that allows us to predict **individual** lane matchup results. Considering the JSON structure present in last section, we will now create one of its many derivatives, with the following structure:


```json
{
    "p_match_id": "BR1_2133967391_jungle",
    "data": [
        {
            "goldEarned": 9414,
            "totalMinionsKilled": 62,
            "win": false,
            "kills": 1,
            "assists": 7,
            "deaths": 8,
            "champion": "Graves",
            "visionScore": 13,
            "puuid": "hRMN6-jyVZAm7nhzYioSiQxy4WfWqhaV7ozDjQZ9OMoE6HSv870_UAtVv6ybRilZGpIdzrz9VmqN-g",
            "totalDamageDealtToChampions": 12217,
            "summonerName": "divespeiro"
        },
        {
            "goldEarned": 10119,
            "totalMinionsKilled": 31,
            "win": true,
            "kills": 3,
            "assists": 10,
            "deaths": 3,
            "champion": "Diana",
            "visionScore": 22,
            "puuid": "UdbGG79WCOn0DkjLv1-dpBZaVxIf3Nt-p9_IdEz5RwCwmj-wOHXSPeserm4uJz5v-RUZnzgleUqgQg",
            "totalDamageDealtToChampions": 9178,
            "summonerName": "soza"
        }
    ],
    "gameVersion": "10.25.348.1797"
}
```

We will store this information inside a new collection called **matchups**. It will only include two players (one from each enemy team), and the API allows us to check in which lane these players played in. For each game (excluding games with AFKs - Away From Keyboard, meaning players that never connected into the game) we will have five different matchups (toplane, midlane, jungle lane, physical damage lane and support lane). If we create this kind of structure, we will be able to check the best competitors for any lane and champion, which will help us make individual predictions and increase the chances of victory in the end. Note that the data available for one specific match will only be able to accurately predict results for a specific patch, since a champion may be optimal for patch 10.25 but really bad on the next one. That's why we also store the matchup game version in our collection structure.

## Statistics

Using an auxiliary file called [find_counts.py](../src/find_counts.py) we can find the number of elements we have in each one of our collections. In my case, having executed the data extraction code for several iterations, and processing matchups, I find myself with the following data:

```
Collection match has 1193746 documents
Collection matchups has 1084470 documents
Collection summoner has 31072 documents
Collection match has 1013284 documents left to process
```

From 31000 players, we have extracted about 1.2 million matches, and from these matches, we have processed only about 200.000 of them (since the matchups collection has an average of five documents per match). It looks like we will not need to download any more new games before processing the remaining matches. We will keep executing the code to increase the dataset for creating the model in the next article.


## Next Steps

After having this data structure, we prepare for the next article, where we will do a deep dive into the training of the model for 1v1 matchups. We will use TensorFlow as the main framework for ML operations, and likely will explore PyTorch to make an introduction to two of the most notable ML libraries available for Python.

Hoping to see you in the next article where we will start training our 1v1 prediction model.

## How can I get started on OCI?

Remember you can always sign up for free to Oracle Cloud Infrastructure: we allow you to sign up for an Oracle Cloud account which provides a number of Always Free services and a Free Trial with US$300 of free credit to use on all eligible Oracle Cloud Infrastructure services for up to 30 days. The Always Free services are available for an **unlimited** period of time. The Free Trial services may be used until your US$300 of free credits are consumed or the 30 days has expired, whichever comes first.

## License
Copyright (c) 2021 Oracle and/or its affiliates.

Licensed under the Universal Permissive License (UPL), Version 1.0.

See [LICENSE](../LICENSE) for more details.

Written by [jasperan](https://github.com/jasperan), edited by Victor Agreda Jr.