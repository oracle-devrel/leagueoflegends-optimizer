# Interacting with leagueoflegends-optimizer

## Introduction
If we want to build an AI/ML model, we need data. For that, Riot Games has provided us with several HTTPs endpoints to make requests and obtain this data. Through the [league.py](../../../src/league.py) file, we'll be able to make all the kinds of requests we want. This Python file has been programmed to allow input parameters and determine the execution mode. 

Estimated Lab Time: xx minutes

### Prerequisites

* An Oracle Free Tier, Paid or LiveLabs Cloud Account
* Active Oracle Cloud Account with available credits to use for Data Science service.

At the time of writing, the following execution modes are available:
  - **`player_list`**: gets the top players from a region and adds them automatically to our database. This includes players above master's elo in League of Legends (really good players), which is the kind of data we want if we're going to build a reliable ML model.
  - **`match_list`**: from all users already present in the database, extract their last 999 matches, or get as many as there are, with the IDs from each one of the games.
  - **`match_download_standard`**: for every ID in the `__match__` collection, get some information about them. This yields data useful to make a 1v1 predictor.
  - **`match_download_detail`**: for every ID in the `__match__` collection, get some global information. This yields data useful to make a 5v5 predictor. It inserts the new data into the `__match_detail__` collection.
  - **`process_predictor`**: uses the `__match_detail__` collection and processes the data to build a pandas-friendly object. Aims to predict a win(1) or a loss(0)
  - **`process_predictor_liveclient`**: similar to **`process_predictor`**, but it has the same column names as the ones we can find in the LiveClient API (what gives us **real-time data**, which means, what we'll be able to use in the end to make real-time predictions)
  - **`process_regressor`**: similar to **`process_predictor`**, but instead of trying to create a classifier model, it attempts to predict winning probability [0,1].
  - **`process_regressor_liveclient`**: similar to **`process_regressor`**, but with LiveClient API-compatible names.
  - **`Default`** mode, which basically performs: **`player_list`** -> **`match_list`** -> **`match_download_standard`** -> **`match_download_detail`**.

## Task 1: Extracting Data / Generating Dataset

There are two components we need to consider in our flow:
- Training process: for this, we need to access historical data, and train a model based on this data.
- Testing process: for this, we need to have a model that's already been trained, and make incoming (new, live) predictions against the model.

1. To extract player data, we can run:
    ```bash
    λ python league.py --mode "player_list"
    >>> Connection successful.
    >>> Region: br1 | Tier: CHALLENGER | Queue: RANKED_SOLO_5x5 | Total Players: 200
    >>> Region: br1 | Tier: GRANDMASTER | Queue: RANKED_SOLO_5x5 | Total Players: 500
    >>> Region: br1 | Tier: MASTER | Queue: RANKED_SOLO_5x5 | Total Players: 3733 
    >>> ...
    ```  
2. This execution mode will iteratively look for League of Legends leaderboards in every region in the world, and insert these players' information into our database. If the user has already been inserted, it will prevent re-insertion.
    > If a user changes their in-game name, the next time the code runs, their new name will be updated in the database. (This is achieved by using their PUUID, a very long identifier instead of their in-game name to identify every player).
3. To extract previously played matches' IDs from our pool of players in the database, we can do this:
    ```bash
    λ python league.py --mode="match_list"
    >>> Connection successful.
    >>> @get_n_match_ids: obtained 0 matches from region europe
    >>> @get_n_match_ids: obtained 0 matches from region europe
    >>> @get_n_match_ids: obtained 0 matches from region americas
    >>> @get_n_match_ids: obtained 0 matches from region americas
    >>> @get_n_match_ids: obtained 0 matches from region asia
    >>> @get_n_match_ids: obtained 0 matches from region asia
    >>> @get_n_match_ids: obtained 0 matches from region europe
    >>> @get_n_match_ids: obtained 0 matches from region europe
    >>> @get_n_match_ids: obtained 269 matches from region americas
    >>> Inserted new match with ID BR1_2410397628 from summoner Josedeodo2 in region americas, queue ranked
    >>> Inserted new match with ID BR1_2399292144 from summoner Josedeodo2 in region americas, queue ranked
    >>> Match ID {'match_id': 'BR1_2392375868'} already inserted
    >>> ...
    ```

    It finds matches played by every player in our database, in every region. This allows us to obtain more matches per player, in case the player travels abroad from their original region, e.g. to compete internationally.

    > This only extracts Match IDs. Processing these IDs is done in the next section

## Task 2: Download Match Details by ID

1. In order to download match details given their IDs, we use the collection __match_detail__. We can process all matches in our current database (found in collection __match__) by executing:
    ```bash
    λ python league.py --mode="match_download_detail"
    >>> Connection successful.
    # it will then start extracting match information.
    # each match contains a huge amount of information, so I'm not putting any examples here, but you'll see when you execute.
    ```
2. This gives us timestamped information about what occurred in each game, in thorough detail. From this, we can build an object with all variables that can be useful in our model.

## Task 3: Building Data Object for ML

We'll use the execution mode _`process_predictor_liveclient`_. This execution mode takes an auxiliary function which creates an object that is compatible with data returned by the Live Client API, which is the API we will access to make real-time match requests. This means that, after this processing, data will have a friendly shape that we can use.

1. [Here you can find the builder object, to check the set of variables that were considered for the model.](../../../src/league.py#L568)
2. Here's how to build the object:
    ```bash
    λ python league.py --mode="process_predictor_liveclient"
    >>> Connection successful.
    >>> Total match_detail documents (to process): 106448
    # resilient to errors, deleted match IDs, etc...
    >>> [DBG] ERR MATCH_ID RETRIEVAL: {'status': {'message': 'Data not found - match file not found', 'status_code': 404}}
    >>> [DBG] ERR MATCH_ID RETRIEVAL: {'status': {'message': 'Service unavailable', 'status_code': 503}}
    # will skip invalid matches
    >>> [DBG] LIVECLIENT BUILDING OBJECT FAILED: 'NoneType' object has no attribute 'get'
    # and insert the ones who are well-formed.
    >>> [DBG] INSERT {'timestamp': 0, 'abilityPower': 0, 'armor': 28, 'armorPenetrationFlat': 0, 'armorPenetrationPercent': 0, 'attackDamage': 25, 'attackSpeed': 100, 'bonusArmorPenetrationPercent': 0, 'bonusMagicPenetrationPercent': 0, 'cooldown
    Reduction': 0, 'currentHealth': 590, 'maxHealth': 590, 'healthRegenRate': 0, 'lifesteal': 0, 'magicPenetrationFlat': 0, 'magicPenetrationPercent': 0, 'magicResist': 32, 'moveSpeed': 335, 'resourceValue': 320, 'resourceMax': 320, 'resource
    RegenRate': 0, 'spellVamp': 0, 'identifier': 'LA2_1049963085_1', 'winner': 0} OK
    ```

You may now [proceed to the next lab](#next).


## Acknowledgements

* **Author** - Nacho Martinez, Data Science Advocate @ DevRel
* **Contributors** -  Victor Martin, Product Strategy Director
* **Last Updated By/Date** - July 10th, 2022
