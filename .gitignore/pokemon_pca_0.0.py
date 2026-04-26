import pandas as pd
import sqlite3
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import plotly.express as px

df = pd.read_csv('python extra\pokemon\All_Pokemon.csv')

''' build DBA
conn = sqlite3.connect("pokemon.db")
df.to_sql("pokemon", conn, if_exists="replace", index=False)
conn.close()'''

#give SQL query
query = """
SELECT * FROM pokemon
"""
conn = sqlite3.connect("pokemon.db")
df = pd.read_sql(query, conn)
print(df)

feature = ['HP','Att','Def','Spa','Spd','Spe']
#x = StandardScaler().fit_transform(df[feature])
#pca = PCA(n_components=2)
#df[['PC1','PC2']] = pca.fit_transform(x)

df['X'] = df['Spe'] - (df['HP'] + df['Def'] + df['Spd']) // 3 
df['Y'] = df[['Att','Spa','Def','Spd']].sum(axis=1)



targets = ['Magikarp', 'Shuckle', 'Gengar']
highlight = df[df['Name'].isin(targets)]

plt.style.use('dark_background')
plt.figure(figsize=(8,8))

plt.scatter(df['X'], df['Y'], color='white')

plt.scatter(highlight['X'], highlight['Y'], s=80, color='lime')

for _, row in highlight.iterrows():
    plt.text(row['X'], row['Y'], row['Name'], color='white')

plt.axhline(300, color='grey')
plt.axvline(0, color='grey')
plt.show()