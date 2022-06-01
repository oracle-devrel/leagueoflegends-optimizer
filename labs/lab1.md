# League of Legends Machine Learning with Oracle - Hands-On Lab

## Introduction

Welcome to this hands-on lab, where we'll talk about how we can leverage the power of AI into League of Legends into a unique an innovative way. We'll do a deep dive into the data that we can extract from the game's API, as well as how to structure this data and how to use it in a Machine Learning model.

TODO IMG

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

## Getting Started

1. We'll also need to obtain a Riot Games API key [from the official Riot Games Developer website.](https://developer.riotgames.com/) For that, you need to create a League of Legends account (if you don't have one already) and ask for a development API key.

![login to your league account](../images/lab1-login.PNG)

2. After creating the account, we [access the development website](https://developer.riotgames.com/) and get our development API key. Note that by default, the development API key expires every 24 hours. So, if you're planning to generate a dataset for more than 24 hours at a time, in the end you'll start getting HTTP unauthorized errors. To fix this, just regenerate the API key and use the new one.

![get api key](../images/lab1-apikey.PNG)

3. After having the API key, we need to create a hidden file in the repository called config.yaml. This file shall contain configuration variables like our API key. This is the format that's been configured in the YAML file in order to be properly parsed inside [the main code of this repository](../src/league.py):

![yaml file structure](../images/lab1-yaml.PNG)
    This file considers that we're using the __cx_Oracle__ Python client to connect to the Autonomous Database. If you're planning on developing a custom Python class and extend the functionalities of this repository, consider using the newest Python thin client to connect to the database, which doesn't require downloading a wallet and its credentials. [Here's the link to the official documentation.](https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html#quickstart)

For that, 



## Extracting Data / Generating Dataset

### Obtaining Player Data

### Obtain Players' Match History Data

