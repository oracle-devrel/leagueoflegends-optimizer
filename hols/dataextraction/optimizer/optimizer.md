# Interacting with leagueoflegends-optimizer

Estimated Time: 30 minutes

## Introduction
If we want to build an AI/ML model, we need data. For that, Riot Games has provided us with several HTTPs endpoints to make requests and obtain this data. Through the [league.py](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/src/league.py) file, we'll be able to make all the kinds of requests we want. This Python file has been programmed to allow input parameters and determine the execution mode. 

> **Note**: all tools mentioned in the optimizer are designed to run **24/7**, meaning that, if you don't stop execution of the optimizer, it will keep collecting data **indefinitely**. You're free to explore with how much data you want to extract using the optimizer. 
<br>
> This means that there's no "end" to the optimizer, it will keep running until you stop it. We recommend going through each task and running each task for **5 minutes** or so if you're getting started; you're free to execute any command at any point afterwards, it won't interfere with already existing data.

### Prerequisites

* An [Oracle Free Tier](https://signup.cloud.oracle.com/?language=en&sourceType=:ow:de:ce::::RC_WWMK220210P00063:LoL_handsonLab_optimizer&intcmp=:ow:de:ce::::RC_WWMK220210P00063:LoL_handsonLab_optimizer), Paid, or LiveLabs Cloud Account
* Active Oracle Cloud Account with available credits to use for Data Science service.

At the time of writing, the following execution modes are available:
  - **`player_list`**: retrieves the top players from a region and adds them automatically to our database. This includes players above master's elo in League of Legends (read: really good players), which is the kind of data we want if we're going to build a reliable ML model.
  - **`match_list`**: from all users already present in the database, extract their last 999 matches, or get as many as there are, with the IDs from each one of the games.
  - **`match_download_standard`**: for every ID in the **`__match__`** collection, get some information about them. This yields data useful to make a 1v1 predictor.
  - **`match_download_detail`**: for every ID in the **`__match__`** collection, get some global information. This yields data useful to make a 5v5 predictor. It inserts the new data into the **`__match_detail__`** collection.
  - **`process_predictor`**: uses the **`__match_detail__`** collection and processes the data to build a pandas-friendly object. Aims to predict a win(1) or a loss(0)
  - **`process_predictor_liveclient`**: similar to **`process_predictor`**, but it has the same column names as the ones we can find in the LiveClient API (what gives us **real-time data**, which means, what we'll be able to use in the end to make real-time predictions)
  - **`process_regressor`**: similar to **`process_predictor`**, but instead of trying to create a classifier model, it attempts to predict winning probability [0,1].
  - **`process_regressor_liveclient`**: similar to **`process_regressor`**, but with LiveClient API-compatible names.
  - **`Default`**: this mode, which basically performs: **`player_list`** -> **`match_list`** -> **`match_download_standard`** -> **`match_download_detail`**.

## Task 1: Extract Data / Generate Dataset

There are two components we need to consider in our flow:
- Training process: for this, we need to access historical data, and train a model based on this data.
- Testing process: for this, we need to have a model that's already been trained, and make incoming (new, live) predictions against the model.

1. To extract player data, we can run:

    ```bash
    λ <copy>python src/league.py --mode "player_list"</copy>
    >>> Connection successful.
    >>> Region: br1 | Tier: CHALLENGER | Queue: RANKED_SOLO_5x5 | Total Players: 200
    >>> Region: br1 | Tier: GRANDMASTER | Queue: RANKED_SOLO_5x5 | Total Players: 500
    >>> Region: br1 | Tier: MASTER | Queue: RANKED_SOLO_5x5 | Total Players: 3733 
    >>> ...
    ```  
This execution mode will iteratively look for League of Legends leaderboards in every region in the world, and insert these players' information into our database. If the user has already been inserted, it will prevent re-insertion.

    If a user changes their in-game name, the next time the code runs, their new name will be updated in the database. (This is achieved by using their PUUID - a very long identifier - instead of their in-game name to identify every player).

2. To extract previously played matches' IDs from our pool of players in the database, we can do this:

    ```bash
    λ <copy>python src/league.py --mode="match_list"</copy>
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

    This command finds matches played by every player in our database, in every region. This allows us to obtain more matches per player, in case the player travels abroad from their original region, e.g. to compete internationally.

    > **Note**: This only extracts Match IDs. Processing these IDs is done in the next section

## Task 2: Download Match Details by ID

1. In order to download match details given their IDs, we use the collection __match_detail__. We can process all matches in our current database (found in collection __match__) by executing:

    ```bash
    λ <copy>python src/league.py --mode="match_download_detail"</copy>
    >>> Connection successful.
    # it will then start extracting match information.
    # each match contains a huge amount of information, so I'm not putting any examples here, but you'll see when you execute.
    ```

2. This gives us timestamped information about what occurred in each game in thorough detail. From this, we can build an object with all variables that can be useful in our model.

## Task 3: Build Data Object for ML

We'll use the __`process_predictor_liveclient`__ execution mode. This execution mode takes an auxiliary function which creates an object that is compatible with data returned by the Live Client API, which is the API we will access to make real-time match requests. This means that, after this processing, data will have a friendly shape that we can use.

1. [Find the builder object here](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/src/league.py#L568). It's with this object that you can check the set of variables that were considered for the model.
2. Here's how to build the object:

    ```bash
    λ <copy>python src/league.py --mode="process_predictor_liveclient"</copy>
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
* **Last Updated By/Date** - February 20th, 2023
