import sqlite3
import pandas as pd
# initializes database definitions and primary key to avoid inserting duplicates into dataset
# you can also use this file to just test stuff, get visualizations from the db. like a query GUI (without the G).
# Connect to the database
conn = sqlite3.connect('example.db')

# Execute SQL statement to add primary key
#results = conn.execute('''select *, count(*) from player_table where summonerName="FOURE7038634357"''') # check if it duplicates. otherwise, perfect.
#print(results.fetchall())
'''
#conn.execute(f'DROP TABLE PLAYER_TABLE') 
definition = 'summonerId REAL PRIMARY KEY, summonerName REAL, leaguePoints REAL, rank REAL, wins REAL, losses REAL, veteran REAL, inactive REAL, freshBlood REAL, hotStreak REAL, tier REAL, request_region REAL, queue REAL'   
conn.execute(f'CREATE TABLE IF NOT EXISTS player_table ({definition})')

conn.execute(f'DROP TABLE match_table') 
definition = 'match_id REAL PRIMARY KEY'   
conn.execute(f'CREATE TABLE IF NOT EXISTS match_table ({definition})')    
'''