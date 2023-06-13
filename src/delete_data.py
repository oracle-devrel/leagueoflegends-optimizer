"""
@author jasperan
This script connects to a SQLite database and deletes rows from the performance_table 
table based on certain conditions.
Specifically, it deletes rows where the value in column f3 is greater than 10.0 or the 
value in column f2 is greater than 4.0 or the value in column f1 is greater than 2.0.
To use this script, make sure to update the path to the database file and the conditions 
for deleting rows as needed.
"""

import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('example.db')

# Read table from sqlite database
result = conn.execute("DELETE FROM performance_table WHERE f3 > 10.0 or f2 > 4.0 or f1 > 2.0")
print(result.rowcount, "rows deleted")

# Commit the changes
conn.commit()


conn.close()