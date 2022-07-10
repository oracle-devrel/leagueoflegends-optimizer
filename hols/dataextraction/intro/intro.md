# Introduction

## Overview
League of Legends is a team-based strategy game where two teams of five powerful champions face off to destroy the other’s base. You can choose from over 140 champions to make epic plays, secure kills, and take down towers as you battle your way to victory. The Nexus is the heart of both teams’ bases. Destroy the enemy’s Nexus first to win the game.

Your team needs to clear at least one lane to get to the enemy Nexus. Blocking your path are defense structures called turrets and inhibitors. Each lane has three turrets and one inhibitor, and each Nexus is guarded by two turrets. In between the lanes is the jungle, where neutral monsters and jungle plants reside. The two most important monsters are Baron Nashor and the Drakes. Killing these units grants unique buffs for your team and can also turn the tide of the game.

There are five positions that make up the recommended team comp for the game. Each lane lends itself to certain kinds of champions and roles—try them all or lock in to the lane that calls you. Champions get stronger by earning experience to level up and gold to buy more powerful items as the game progresses. Staying on top of these two factors is crucial to overpowering the enemy team and destroying their base.

In this lab, we will leverage with the power of AI with League of Legends in a unique an innovative way. We'll do a deep dive into the extractable data through the game's API, as well as how to structure this data, and how to use it to train our own Machine Learning model to generate real-time predictions about any match.

![Bought Items](images/bought_items.jpg)

The above image represents the final functionality of this workshop, where we're able to use our already-trained ML model to make real-time predictions about our in-game performances. 

We'll also need to create an autonomous database. We'll use it as our storage for our generated datasets and access points as a whole.

In this Hands-On Lab (HOL), we'll start from the assumption that people know about how League of Legends' matchmaking system works. If you have time and don't know a lot about League of Legends, I recommended reading these lists of articles (included in the repository as well) to get a feel of what we'll talk about in the HOL:

1. [Article 1](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/main/articles/article1.md): League of Legends Optimizer using Oracle Cloud Infrastructure: Data Extraction & Processing
2. [Article 2](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/main/articles/article2.md): League of Legends Optimizer using Oracle Cloud Infrastructure: Data Extraction & Processing II
3. [Article 3](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/main/articles/article3.md): League of Legends Optimizer using Oracle Cloud Infrastructure: Building an Adversarial League of Legends AI Model
4. [Article 4](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/main/articles/article4.md): League of Legends Optimizer using Oracle Cloud Infrastructure: Real-Time predictions
5. [Article 5](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/main/articles/article5.md): League of Legends Optimizer using Oracle Cloud Infrastructure: Real-Time predictions II


Estimated Lab Time: xx minutes


### Prerequisites

* An Oracle Free Tier, Paid or LiveLabs Cloud Account
* Active Oracle Cloud Account with available credits to use for Data Science service.


## Task 1: Get Started

1. If you don't have a League of Legends account, you'll need to register and download the videogame. 

1. We'll need to obtain a Riot Games API key [from the official Riot Games Developer website.](https://developer.riotgames.com/) For that, you need to create a League of Legends account (if you don't have one already) and ask for a development API key. Note that if you're planning to develop a League of Legends project out of this repository, you can also apply for a production API key which has a longer expiration date, as well as more requests per minute.
    ![login to your league account](images/lab1-login.png)
2. After creating the account, we [access the development website](https://developer.riotgames.com/) and get our development API key. Note that by default, the development API key expires every 24 hours. So, if you're planning to generate a dataset for more than 24 hours at a time, in the end you'll start getting HTTP unauthorized errors. To fix this, just regenerate the API key and use the new one.
    ![get api key](images/lab1-apikey.png)
3. After having the API key, we need to create a hidden file in the repository called config.yaml. This file shall contain configuration variables like our API key. This is the format that's been configured in the YAML file in order to be properly parsed inside [the main code of this repository](../src/league.py):
    ![yaml file structure](images/lab1-yaml.png)

    > This file considers that we're using the latest __python-oracledb__ thin/thick Python client to connect to the Autonomous Database. [Here's the link to the official documentation.](https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html#quickstart)
4. To check the validity of our YAML file settings, we can run [a sample program](../../../src/test_newclient.py) against the database, to check whether we can connect to it successfully or not.
    ```bash
    cd src/
    python test_newclient.py 
    # this will return the current date if you were able to successfully connect to the database.
    >>> (datetime.datetime(2022, 6, 1, 21, 11, 40)) # when I executed it.
    ```
5. After checking that we can successfully connect to the database, it's time to get started with the cool stuff.

You may now [proceed to the next lab](#next).


## Acknowledgements

* **Author** - Nacho Martinez, Data Science Advocate @ DevRel
* **Contributors** -  Victor Martin, Product Strategy Director
* **Last Updated By/Date** - July 10th, 2022