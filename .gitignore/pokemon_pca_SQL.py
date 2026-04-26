import pandas as pd
import sqlite3
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
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

type_colors = {
    "Bug": "#94bc4a",
    "Dark": "#736c75",
    "Dragon": "#6a7baf",
    "Electric": "#e5c531",
    "Fairy": "#e397d1",
    "Fighting": "#cb5f48",
    "Fire": "#ea7a3c",
    "Flying": "#7da6de",
    "Ghost": "#846ab6",
    "Grass": "#71c558",
    "Ground": "#cc9f4f",
    "Ice": "#70cbd4",
    "Normal": "#aab09f",
    "Poison": "#b468b7",
    "Psychic": "#e5709b",
    "Rock": "#b2a061",
    "Steel": "#89a1b0",
    "Water": "#539ae2"
}
#x = StandardScaler().fit_transform(df[feature])
#pca = PCA(n_components=2)
#df[['PC1','PC2']] = pca.fit_transform(x)

df['X'] = df['Spe'] - (df['HP'] + df['Def'] + df['Spd']) / 3 
df['Y'] = df[['Att','Spa','Def','Spd']].sum(axis=1)
df['type_display'] = df.apply(
    lambda r: r['Type 1'] if pd.isna(r['Type 2']) else f"{r['Type 1']}/{r['Type 2']}",
    axis=1
)

query = """
SELECT Name FROM pokemon
WHERE Name = 'Venusaur'
"""
highlight_df = pd.read_sql(query, conn)
targets = highlight_df['Name'].tolist()

fig = px.scatter(
    df,
    x='X',
    y='Y',
    hover_name='Name',
    custom_data = ['HP','Att','Def','Spa','Spd','Spe','type_display','BST','Generation','Height','Weight'],
    color = df['Name'].isin(targets),
    color_discrete_map={
        True: 'yellow',
        False: 'white'
    }
)

fig.update_layout(
    template='plotly_dark',
    xaxis_title="<--Tank-Speed-->", 
    yaxis_title="<--Strong-->"
)
fig.update_traces(
    hovertemplate=
    "<b>%{hovertext}</b> Gen %{customdata[8]}<br>" +
    "Height: %{customdata[9]}m Weight: %{customdata[10]}kg<br>" +
    #"<img src='%{customdata[7]}' width='90'><br>" +
    "Type: %{customdata[6]}<br>" +
    "HP: %{customdata[0]}<br>" +
    "Atk: %{customdata[1]}<br>" +
    "Def: %{customdata[2]}<br>" +
    "SpA: %{customdata[3]}<br>" +
    "SpD: %{customdata[4]}<br>" +
    "Spe: %{customdata[5]}<br>" +
    "BST: %{customdata[7]}<br>" +
    "<extra></extra>"
)
fig.update_xaxes(
    range=[(df['X'].min() // 50) * 50, ((df['X'].max() // 50) + 1) * 50],
    autorange=False
)

fig.update_yaxes(
    range=[(df['Y'].min() // 100) * 100, ((df['Y'].max() // 100) + 1) * 100],
    autorange=False
)
fig.show()