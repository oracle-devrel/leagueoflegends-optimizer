# Getting Started

## Introduction
TODO

Estimated Lab Time: xx minutes

### Prerequisites

* An Oracle Free Tier, Paid or LiveLabs Cloud Account
* Active Oracle Cloud Account with available credits to use for Data Science service.

## Task 1: Getting Started

TODO

1. We'll also need to obtain a Riot Games API key [from the official Riot Games Developer website.](https://developer.riotgames.com/) For that, you need to create a League of Legends account (if you don't have one already) and ask for a development API key. Note that if you're planning to develop a League of Legends project out of this repository, you can also apply for a production API key which has a longer expiration date, as well as more requests per minute.
    ![login to your league account](images/lab1-login.png)
2. After creating the account, we [access the development website](https://developer.riotgames.com/) and get our development API key. Note that by default, the development API key expires every 24 hours. So, if you're planning to generate a dataset for more than 24 hours at a time, in the end you'll start getting HTTP unauthorized errors. To fix this, just regenerate the API key and use the new one.
    ![get api key](images/lab1-apikey.png)
3. After having the API key, we need to create a hidden file in the repository called config.yaml. This file shall contain configuration variables like our API key. This is the format that's been configured in the YAML file in order to be properly parsed inside [the main code of this repository](files/league.py):
    ![yaml file structure](images/lab1-yaml.png)

    > This file considers that we're using the latest __python-oracledb__ thin/thick Python client to connect to the Autonomous Database. [Here's the link to the official documentation.](https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html#quickstart)
4. To check the validity of our YAML file settings, we can run [a sample program](files/test_newclient.py) against the database, to check whether we can connect to it successfully or not.
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
* **Last Updated By/Date** - 
