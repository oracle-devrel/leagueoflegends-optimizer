# League of Legends Machine Learning with Oracle - Building a DataSet and Extracting Data - Hands-On Lab

## Introduction

Welcome to this hands-on lab, where we'll talk about how we can leverage the power of AI with League of Legends in a unique an innovative way. We'll do a deep dive into the extractable data through the game's API, as well as how to structure this data, and how to use it to train our own Machine Learning model to generate real-time predictions about any match.

![Bought Items](https://raw.githubusercontent.com/oracle-devrel/leagueoflegends-optimizer/main/images/bought_items.JPG?raw=true)
G

The above image represents the final functionality of [this repository](https://github.com/oracle-devrel/leagueoflegends-optimizer), where we're able to use our already-trained ML model to make real-time predictions about our in-game performances. 

In this Hands-On Lab (HOL), we'll start from the assumption that people know about how League of Legends' matchmaking system works. If you have time and don't know a lot about League of Legends, I recommended reading these lists of articles (included in the repository as well) to get a feel of what we'll talk about in the HOL:
- [Article 1](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/main/articles/article1.md): League of Legends Optimizer using Oracle Cloud Infrastructure: Data Extraction & Processing
- [Article 2](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/main/articles/article2.md): League of Legends Optimizer using Oracle Cloud Infrastructure: Data Extraction & Processing II
- [Article 3](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/main/articles/article3.md): League of Legends Optimizer using Oracle Cloud Infrastructure: Building an Adversarial League of Legends AI Model
- [Article 4](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/main/articles/article4.md): League of Legends Optimizer using Oracle Cloud Infrastructure: Real-Time predictions
- [Article 5](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/main/articles/article5.md): League of Legends Optimizer using Oracle Cloud Infrastructure: Real-Time predictions II


## Prerequisites

You'll need an OCI free trial account to develop some of the things we will talk about in this lab (<a href="https://signup.cloud.oracle.com/?sourceType=_ref_coc-asset-opcSignIn&language=en_US" target="_blank" title="Sign up for free trial">click here to sign up</a>).

Registered lab participants should have received $300 in credits to use for Data Science operations.

### SSH Key for Compute Instance

You'll also need an SSH key pair to access the OCI Compute Instance we're going to create. For Mac/Linux systems, you can [use `ssh-keygen`](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/managingkeypairs.htm#ariaid-title4). On Windows, you'll [use PuTTY Key Generator](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/managingkeypairs.htm#ariaid-title5). 

To summarize Mac/Linux:

    ssh-keygen -t rsa -N "" -b 2048 -C "<key_name>" -f <path/root_name> 

For Windows, and step-by-step instructions for Mac/Linux, please see the [Oracle Docs on Managing Key Pairs](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/managingkeypairs.htm#Managing_Key_Pairs_on_Linux_Instances).

### Autonomous Database

We'll also need to create an autonomous database. We'll use it as our storage for our generated datasets and access points as a whole.

To create an autonomous database, [follow the steps in this video](https://www.youtube.com/watch?v=JOcmoXE1zqY).

After creating the autonomous database, you should have access to this panel in OCI:

![menu](../images/lab1-menu.PNG)

At the panel, we're going to modify a couple of network settings to allow us to connect using TLS instead of m-TLS (mutual TLS). Long story short, using TLS instead of mTLS will make the task of connecting to the database easier (and additionally, it makes it possible to connect and use the __python-oracledb__ thin client if we want to, instead of only using the Thick client). Note that activating TLS as the authentication mechanism doesn't restrict us from connecting using mTLS still, it just expands our possibilities of connecting
    **Note**: mTLS will use port 1522 by default and TLS will use port 1521. If you're in a machine with firewall activated, make sure that in/egress firewall rules are suited for those ports.

So, we will need to modify the Access Control List (ACL) to allow our own IP address to connect to the database (or whichever IP you want). In my case, I've added the most unrestrictive CIDR block, so that anyone can make a request with the proper username/password/connection string, by adding the CIDR block 0.0.0.0/0 (all IPs):

![acl](../images/lab1-acl.PNG)


And finally, disable the parameter that "requires" us to connect through mTLS, and make TLS authentication also possible:

![tls](../images/lab1-tls.PNG)

Finally, after the database has finished updating, we can access the "DB Connection" section on top, and get our connection strings:

![database connection](../images/lab1-dbconnection.PNG)

Note that we want our TLS connection strings (not mTLS connection strings) as they are different.

![TLS connection strings](../images/lab1-connectionstrings.PNG)

You can use any of the connection strings available, just note that the __tpurgent__ connection strings supports parallel calls and many more operations per second compared to all other connection strings. It's reserved for urgent operations, but since we're the only ones who are going to use the database, and just for this use case, let's not worry about prioritizing our tasks for now.

So, in my case, an example connection string would be:

```bash
(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=XXXXXXXXXXXX))(connect_data=(service_name=XXXXXXXXXXXXXXXX))(security=(ssl_server_dn_match=yes)(ssl_server_cert_dn="CN=XXXXXXXXXXXXX, OU=XXXXX, O=XXXXX XXXXXX, L=Redwood XXXXX, ST=XXXX, C=XXXX")))
```
Let's make note of this as well, as we'll need to add this to our configuration file later on.

### Downloading Instant Client

As we're going to want to connect to our newly created Autonomous Database, we also need to consider the supporting Oracle packages required to support this connection. This is facilitated by Oracle Instant Client, which we'll need to install. 

Depending on the Operating System where you are, you'll need to download your respective binary files from [this link](https://www.oracle.com/database/technologies/instant-client/downloads.html). After installing Instant Client, we'll need to unzip the file into a directory (and remember the directory in which we put the unzipped file, we'll need to use it as a configuration parameter). 

In the end, your installation should look something like this:

![instant client](../images/lab1-instantclient.PNG)

And, in my case, my path to my instant client installation would be:

```bash
D:\Programs\instantclient
```
Which is what we'll use in our configuration file.

### Downloading Wallet

After setting up the Autonomous Database, we need to download the client credentials (required by design for mTLS connections). 

After downloading it, we'll copy all the contents that we found inside our Instant Client installation folder.

Recalling the directory:

```bash
D:\Programs\instantclient
```

So, in my case, I'd paste the contents of the wallet into:

```bash
D:\Programs\instantclient\network\admin\
```

Finally, I'll modify the contents of **sqlnet.ora** to make sure that the Python thick client can find the files it needs to connect through mTLS. 

By default, the file has these contents:

```bash
WALLET_LOCATION = (SOURCE = (METHOD = file) (METHOD_DATA = (DIRECTORY="?/network/admin")))
SSL_SERVER_DN_MATCH=yes
```

I'll replace this with the specified directory where my wallet has been placed, and leave no place for error:

```bash
WALLET_LOCATION = (SOURCE = (METHOD = file) (METHOD_DATA = (DIRECTORY="D:/Programs/instantclient/network/admin")))
SSL_SERVER_DN_MATCH=yes
```

## Getting Started

1. We'll also need to obtain a Riot Games API key [from the official Riot Games Developer website.](https://developer.riotgames.com/) For that, you need to create a League of Legends account (if you don't have one already) and ask for a development API key. Note that if you're planning to develop a League of Legends project out of this repository, you can also apply for a production API key which has a longer expiration date, as well as more requests per minute.

![login to your league account](../images/lab1-login.PNG)

2. After creating the account, we [access the development website](https://developer.riotgames.com/) and get our development API key. Note that by default, the development API key expires every 24 hours. So, if you're planning to generate a dataset for more than 24 hours at a time, in the end you'll start getting HTTP unauthorized errors. To fix this, just regenerate the API key and use the new one.

![get api key](../images/lab1-apikey.PNG)

3. After having the API key, we need to create a hidden file in the repository called config.yaml. This file shall contain configuration variables like our API key. This is the format that's been configured in the YAML file in order to be properly parsed inside [the main code of this repository](../src/league.py):

![yaml file structure](../images/lab1-yaml.PNG)

This file considers that we're using the latest __python-oracledb__ thin/thick Python client to connect to the Autonomous Database. [Here's the link to the official documentation.](https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html#quickstart)

4. To check the validity of our YAML file settings, we can run [a sample program](../src/test_newclient.py) against the database, to check whether we can connect to it successfully or not.

```bash
cd src/
python test_newclient.py 
# this will return the current date if you were able to successfully connect to the database.
>>> (datetime.datetime(2022, 6, 1, 21, 11, 40)) # when I executed it.
```

5. After checking that we can successfully connect to the database, it's time to get started with the cool stuff.

## Interacting with leagueoflegends-optimizer

If we want to build an AI/ML model, we need data. For that, Riot Games has provided us with several HTTPs endpoints to make requests and obtain this data. Through the [league.py](../src/league.py) file, we'll be able to make all the kinds of requests we want. This Python file has been programmed to allow input parameters and determine the execution mode. 

At the time of writing, the following execution modes are available:
- **player_list**: gets the top players from a region and adds them automatically to our database. This includes players above master's elo in League of Legends (really good players), which is the kind of data we want if we're going to build a reliable ML model.
- **match_list**: from all users already present in the database, extract their last 999 matches, or get as many as there are, with the IDs from each one of the games.
- **match_download_standard**: for every ID in the __match__ collection, get some information about them. This yields data useful to make a 1v1 predictor.
- **match_download_detail**: for every ID in the __match__ collection, get some global information. This yields data useful to make a 5v5 predictor. It inserts the new data into the __match_detail__ collection.
- **process_predictor**: uses the __match_detail__ collection and processes the data to build a pandas-friendly object. Aims to predict a win(1) or a loss(0)
- **process_predictor_liveclient**: similar to **process_predictor**, but it has the same column names as the ones we can find in the LiveClient API (what gives us **real-time data**, which means, what we'll be able to use in the end to make real-time predictions)
- **process_regressor**: similar to **process_predictor**, but instead of trying to create a classifier model, it attempts to predict winning probability [0,1].
- **process_regressor_liveclient**: similar to **process_regressor**, but with LiveClient API-compatible names.
- **Default** mode, which basically performs: **player_list** -> **match_list** -> **match_download_standard** -> **match_download_detail**.

## Extracting Data / Generating Dataset

There are two components we need to consider in our flow:
1. Training process: for this, we need to access historical data, and train a model based on this data.
2. Testing process: for this, we need to have a model that's already been trained, and make incoming (new, live) predictions against the model.

#### Player Data
To extract player data, we can run:

```bash
λ python league.py --mode "player_list"
>>> Connection successful.
>>> Region: br1 | Tier: CHALLENGER | Queue: RANKED_SOLO_5x5 | Total Players: 200
>>> Region: br1 | Tier: GRANDMASTER | Queue: RANKED_SOLO_5x5 | Total Players: 500
>>> Region: br1 | Tier: MASTER | Queue: RANKED_SOLO_5x5 | Total Players: 3733 
>>> ...
```
This execution mode will iteratively look for League of Legends leaderboards in every region in the world, and insert these players' information into our database. If the user has already been inserted, it will prevent re-insertion. 
    **Note**: if a user changes their in-game name, the next time the code runs, their new name will be updated in the database. (This is achieved by using their PUUID, a very long identifier instead of their in-game name to identify every player).

#### Players' Match History Data
To extract previously played matches' IDs from our pool of players in the database, we can do this:

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

**Note**: this only extracts Match IDs. Processing these IDs is done in the next section

### Download Match Details by ID

For that, we use the collection __match_detail__. We can process all matches in our current database (found in collection __match__) by executing:

```bash
λ python league.py --mode="match_download_detail"
>>> Connection successful.
# it will then start extracting match information.
# each match contains a huge amount of information, so I'm not putting any examples here, but you'll see when you execute.
```

This gives us timestamped information about what occurred in each game, in thorough detail. From this, we can build an object with all variables that can be useful in our model. For that, 


### Building Data Object for ML

We'll use the execution mode __process_predictor_liveclient__. This execution mode takes an auxiliary function which creates an object that is compatible with data returned by the Live Client API, which is the API we will access to make real-time match requests. This means that, after this processing, data will have a friendly shape that we can use.

[Here you can find the builder object, to check the set of variables that were considered for the model.](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/1/src/league.py#L568)

Here's how to build the object:

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

## Live Client API

To extract live game information, we need to access the Live Client Data API from Riot Games.

The League Client API involves a set of protocols that CEF (Chromium Embedded Framework) uses to communicate between the League of Legends process and a C++ library.

![](https://static.developer.riotgames.com/img/docs/lol/lcu_architecture.png?raw=true)

Communication between the CEF and this C++ library happen locally, so we're obligated to use localhost as our connection endpoint. You can find additional information about this communication [here.](https://developer.riotgames.com/docs/lol)

You can also refer back to [article 4](../articles/article4.md), where I explain the most interesting endpoints that we encounter when using the Live Client Data API. 

For this article, we'll use the following endpoint:

```python
# GET https://127.0.0.1:2999/liveclientdata/allgamedata
# Sample output can be found in the following URL, if interested. https://static.developer.riotgames.com/docs/lol/liveclientdata_sample.json
# This endpoint encapsulates all other endpoints into one.
```

When we join a League of Legends game, the League process opens port 2999. We'll use this to our advantage and we'll make recurring requests to localhost:2999 to extract live match information.

### Testing the Live Client API

If you want to test the Live Client API, you'll need to join a League of Legends match:

![league loading screen](../images/lab1-league1.PNG)

After clicking on "play", we'll create a custom match and set to play against an AI bot:

![creating match](../images/lab1-league2.PNG)

![creating match 2](../images/lab1-league3.PNG)

![in game](../images/lab1-league4.PNG)


After joining the game, we can start making HTTP requests to check our live champion statistics, score, cooldowns, etc. [To make the requests automatically, you can use this code.](../src/live_client_producer.py)
[This is an example packet returned by the Live Client API](https://static.developer.riotgames.com/docs/lol/liveclientdata_sample.json) and we can observe the kind of information we can access from a player. I've attached the obtained sample from the screenshots above [in this file](../src/aux_files/example_live_client.txt).

```json
{
    "magicResist": 32,
    "healthRegenRate": 0,
    "spellVamp": 0,
    "timestamp": 0,
    "bonusArmorPenetrationPercent": 0,
    "bonusMagicPenetrationPercent": 0,
    "maxHealth": 540,
    "moveSpeed": 335,
    "attackDamage": 25,
    "armorPenetrationPercent": 0,
    "lifesteal": 0,
    "abilityPower": 0,
    "cooldownReduction": 0,
    "resourceValue": 350,
    "magicPenetrationFlat": 0,
    "attackSpeed": 100,
    "currentHealth": 540,
    "armor": 35,
    "magicPenetrationPercent": 0,
    "armorPenetrationFlat": 0,
    "resourceMax": 350,
    "resourceRegenRate": 0
}
```

All this champion information is the information we'll use as input in our ML model. So, we need to harmonize column names and amount of variables in our pre-trained models, with the information we have available in real-time, so that the ML model can make predictions with everything available. This is achieved thanks to the __process_predictor_liveclient__ function.

This is all we have for the first session. A recap of what we have learned is:
- How to provision resources in OCI for Data Science purposes
- How to create a datastore architecture for our problems
- How to data mine League of Legends through an API
- How to build and structure the data
- How to connect to the Live Client API