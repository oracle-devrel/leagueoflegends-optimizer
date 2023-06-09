# Copyright (c) 2022 Oracle and/or its affiliates.

'''
@author jasperan
This file connects to an Oracle Autonomous Database and checks all connectivities:
- Riot Games API -> makes a request against the API key to check if we are authorized
- DB Connectivity -> creates a connection to see if the wallet and database are properly configured

Requires a wallet ZIP file and credentials to use it.

'''
import os
import requests
import oracledb
from dotenv import load_dotenv
from colors import color

load_dotenv()

ok_string = color('OK:\t', fg='green')
fail_string = color('FAIL:\t', fg='red')

oracledb_user = os.getenv("DB_USER")
oracledb_password = os.getenv("DB_PASSWORD")
oracledb_connection_string = os.getenv("CONNECTION_STRING")
riot_api_key = os.getenv("RIOT_API_KEY")


def db_connectivity():
    connection = oracledb.connect(
        user=oracledb_user, password=oracledb_password, dsn=oracledb_connection_string)
    cursor = connection.cursor()
    sql = """select sysdate from dual"""

    try:
        cursor.execute(sql)
        print(f'{ok_string}DB Connectivity')
    except Exception as e:
        print(f'{fail_string}DB Connectivity: {e.args.message}')


def riot_api_connectivity():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://developer.riotgames.com",
        "X-Riot-Token": riot_api_key
    }
    region = "eun1"
    request_url = f'https://{region}.api.riotgames.com/lol/status/v4/platform-data'
    try:
        response = requests.get(request_url, headers=headers)
        if response.status_code == 200:
            print(f'{ok_string}Riot API')
        else:
            response_message = response.json()['status']['message']
            print(
                f'{fail_string}Riot API: HTTP {response.status_code} {response_message}')
    except Exception as e:
        print(f'{fail_string}Riot API: {e.args.message}')


def main():
    print("Checking setup...")
    db_connectivity()
    riot_api_connectivity()


if __name__ == '__main__':
    main()
