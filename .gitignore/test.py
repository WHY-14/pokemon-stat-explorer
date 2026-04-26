import pandas as pd
import sqlite3

query = """
SELECT Name, "Mega Evolution"
FROM pokemon
WHERE Name LIKE '%Mega%' OR Name LIKE '%Primal%'
"""
conn = sqlite3.connect("pokemon.db")
df = pd.read_sql(query, conn)
print(df.to_string())
conn.close()