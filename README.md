# League of Legends Optimizer

[![License: UPL](https://img.shields.io/badge/license-UPL-green)](https://img.shields.io/badge/license-UPL-green) [![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=oracle-devrel_leagueoflegends-optimizer)](https://sonarcloud.io/dashboard?id=oracle-devrel_leagueoflegends-optimizer)

## Introduction
The data extraction process has been evaluated using the official Riot Games API. There's a lot of information available. From this initial set of data I have devised two ways of approaching and helping Tyler's League of Legends team:
1. Extract offline data from players, matches and accounts from the "Offline" API; and create a ML model to predict the outcome of games based on compositions and game versions. There's loads of information about champion stats from each version so it makes sense that data and models should be trained only on patches, or patches where champion statistics change. Another good idea would be to use external tier lists of champions to weigh the compositions depending on the importance of a champion in a patch.
2. Extract live data using the [Live Client Data API](https://developer.riotgames.com/docs/lol#game-client-api_live-client-data-api) and see what we can do. Maybe there's additional information like the snowball effect from jungle monsters, baron nashor and drakes. 

## Live Client Data API

The Live Client Data API provides a method for gathering data during an active game. It includes general information about the game as well player data.

The Live Client Data API has a number of endpoints that return a subset of the data returned by the /allgamedata endpoint. This endpoint is great for testing the Live Client Data API, but unless you actually need all the data from this endpoint, we suggest one of the endpoints listed below that return a subset of the response. 

Currently, the information which can be extracted from the Live Client Data API contains:
- Current player statistics, abilities and their levels, gold and player level at (supposedly) any given time in the game. With this, we could create the snowball effect by ourselves if it's not explicitly included.
- Current runes for the player 
- List of heroes in the game and their stats (scores, skins, spells, position they are playing in, dead or alive, and current items of players).
- Current score for each player (assists, minion farm score, deaths, kills and ward score). From this we could also derive some information like ward impact at each stage of the game. It would be good to try to figure out if it's possible to check in real time when turrets have been destroyed to change from early to middle and late game stages; or speak with Tyler on which factors contribute to a change of stages in the game. Typically earlygame is constituted between the first 12 to 14 minutes in the game, but let's make sure of this talking with Tyler.
- Every player's runes, spells, items (in cooldown or not, slot placement)
- List of events that have happened since the beginning of the game (such as game start). These are all the [events](https://static.developer.riotgames.com/docs/lol/liveclientdata_events.json).
- Basic data about the game (map, game time, type of queue in which the match is being played in, and map terrain information).


### Available endpoints
There are many available endpoints for the Live Client Data API, but the one that encapsulates the information from all sources is the following:

#### Get All Game Data

The Live Client Data API has a number of endpoints that return a subset of the data returned by the /allgamedata endpoint. This endpoint is great for testing the Live Client Data API, but unless you actually need all the data from this endpoint, it is suggested to use one of the endpoints listed below, which return a subset of the response.

GET https://127.0.0.1:2999/liveclientdata/allgamedata

### Ideas
For the future, we would like to expand this functionality to create a tool that allows to visualize:
1. Snowball effect after a large monster kill
2. Jungle gold difference impact in the game (carry potential)


## Getting Started

### Prerequisites
Requirements file can be found in /requirements.txt. You will also need to have installed Oracle Instant Client or other means of connectivity to the Oracle Autonomous JSON Database. After installing both, you should be able to run the code inside `src/`.

### Running the code
Run:
`python3 league.py` for the full process. You can modify your code to run all components or just the ones you need in the data_mine() function.


## Notes/Issues
* Nothing at this moment

## URLs
[Riot Games API](https://developer.riotgames.com/)

## Contributing
This project is open source.  Please submit your contributions by forking this repository and submitting a pull request!  Oracle appreciates any contributions that are made by the open source community.

## License
Copyright (c) 2021 Oracle and/or its affiliates.

Licensed under the Universal Permissive License (UPL), Version 1.0.

See [LICENSE](LICENSE) for more details.






