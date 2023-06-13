'''
@author jasperan
This file reads from the example.db sqlite3 database,
and then puts the contents of the three tables into a separate CSV file
in order to load them into a pandas dataframe later on in the ML process.
'''

import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('example.db')

# Read table from sqlite database
df = pd.read_sql_query('SELECT * FROM performance_table', conn)
print(df.tail())
pd.set_option('display.max_columns', None)
print(df.iloc[-1]['summonerId'])
print(len(df))

df.to_csv('performance_report.csv', index=True)

# Read table from sqlite database
df = pd.read_sql_query('SELECT * FROM player_table', conn)

print(df.tail())

print(len(df))

df.to_csv('player_report.csv', index=True)

# Read table from sqlite database
df = pd.read_sql_query('SELECT * FROM match_table', conn)

print(df.tail())

print(len(df))

# Export it to csv
df.to_csv('match_report.csv', index=True)

#         #print(', '.join([f'{key} REAL' for key in final_object.keys()])) # get header for sql 
# create definitions for creation