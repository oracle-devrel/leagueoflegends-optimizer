# Interacting with leagueoflegends-optimizer

Estimated Time: 30 minutes

## Introduction
If we want to build an AI/ML model, we need data. Lots and lots of data.

For that, Riot Games has provided us with several HTTPs endpoints to make requests and obtain this data. Through the [league.py](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/src/league.py) file, we'll be able to make all the kinds of requests we want. This Python file has been programmed to allow input parameters and determine the execution mode. 

All tools mentioned in this lab are designed to allow parallel and continuous execution, meaning that, if you don't stop execution of the optimizer, it will keep collecting data **indefinitely**. You're free to explore with how much data you want to extract using the optimizer. 

This means that there's no "end" to the optimizer, it will keep running until you stop it, achieving more and more data if you keep it running.

We recommend going through each task and running each task for **5 minutes** or so if you're getting started; you're free to execute any command at any point afterwards, it won't interfere with already existing data.


### Prerequisites

* An [Oracle Free Tier](https://signup.cloud.oracle.com/?language=en&sourceType=:ow:de:ce::::RC_WWMK220210P00063:LoL_handsonLab_optimizer&intcmp=:ow:de:ce::::RC_WWMK220210P00063:LoL_handsonLab_optimizer), Paid, or LiveLabs Cloud Account
* Active Oracle Cloud Account with available credits to use for Data Science service.

### Objectives

In this lab, you will learn how to:
- Learn about what an API is and how it's accessed
- Extract different data types from Riot Games' API
- Manipulate the data to make it ML-ready
- Use this data to generate CSV datasets to later process
  

## Task 1: Extract Data / Generate Dataset

There are some things to consider. In League of Legends, and since there are several endpoints, in order to extract data, we will need to:
1. Get some players' information (their unique identifiers). Note that we will only operate with players above Masters elo, to reduce variability of finding mistakes in play in our dataset.
2. For each player, obtain their most recently played matches
3. For each match, extract its detailed report from the API
4. Format this data properly and store it
5. Repeat forever

The more you repeat this process, the more data your dataset will have. If you want to use my dataset, [check out this Kaggle dataset](https://www.kaggle.com/datasets/jasperan/league-of-legends-optimizer-dataset?select=sqlite_report_performance.csv) or refer to the Infrastructure lab to download it (step 6) if you haven't already.


1. To extract player data, we can run:

    ```bash
    λ <copy>python src/sqlite_league.py --mode "player_list"</copy>
    ```  

    ![player list result](images/result-player-list.png)
    > **Note**: note that in this case, since my dataset is already big enough, most players I extract are already in my database. It's recommended to run this every few months to get newer players, but variability above Masters elo is low.


This execution mode will iteratively look for League of Legends leaderboards in every region in the world, and insert these players' information into our database. If the user has already been inserted, it will prevent re-insertion.

2. To extract previously played matches' IDs from our pool of players in the database, we can do this:

    ```bash
    λ <copy>python src/league.py --mode="match_list"</copy>
    ```

    ![match list result](images/result-match-list.png)



    This command finds matches played by every player in our database, in every region. This allows us to obtain more matches per player, in case the player travels abroad from their original region, e.g. to compete internationally.

    > **Note**: This only extracts Match IDs. Processing these IDs is done in the next section


## Task 2: Process Player Performance

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
* **Last Updated By/Date** - May 18th, 2023