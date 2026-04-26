import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc

#載入資料
conn = sqlite3.connect("pokemon.db")
df = pd.read_sql("SELECT * FROM pokemon", conn)
conn.close()

type_colors = {
    "Bug": "#94bc4a", "Dark": "#736c75", "Dragon": "#6a7baf",
    "Electric": "#e5c531", "Fairy": "#e397d1", "Fighting": "#cb5f48",
    "Fire": "#ea7a3c", "Flying": "#7da6de", "Ghost": "#846ab6",
    "Grass": "#71c558", "Ground": "#cc9f4f", "Ice": "#70cbd4",
    "Normal": "#aab09f", "Poison": "#b468b7", "Psychic": "#e5709b",
    "Rock": "#b2a061", "Steel": "#89a1b0", "Water": "#539ae2"
}

#建立X,Y / 補資料
df['X'] = (df['Spe'] + df['Spa'] + df['Att']) / 3 - (df['HP'] + df['Def'] + df['Spd']) / 3
df['Y'] = df['BST']
df['type_display'] = df.apply(
    lambda r: r['Type 1'] if pd.isna(r['Type 2']) else f"{r['Type 1']}/{r['Type 2']}",
    axis=1
)

all_types = sorted(type_colors.keys())
all_gens  = sorted(df['Generation'].dropna().unique().astype(int).tolist())

X_RANGE = [(df['X'].min() // 50) * 50,  ((df['X'].max() // 50) + 1) * 50]
Y_RANGE = [(df['Y'].min() // 100) * 100, ((df['Y'].max() // 100) + 1) * 100]

#外觀
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

#fix colour palette
app.index_string = app.index_string.replace(
    '</head>',
    '''<style>
        .dash-input-container { background-color: #222 !important; color: #ccc !important; border: 1px solid #444 !important; }
        .dash-dropdown-search-container { background-color: #222 !important; color: #ccc !important; border: 1px solid #444 !important; }
        /* Dropdown 背景 */
        .dash-dropdown-grid-container { background-color: #222 !important; border-color: #444 !important; }
        /* 文字 */
        .dash-dropdown-value { color: #ccc !important; }
        .dash-options-list-option-text { color: #ccc !important; }
        .dash-dropdown-action-button { color: #ccc !important; }
        /* 展開選單背景 */
        .dash-options-list { background-color: #222 !important; border-color: #444 !important; }
        .dash-dropdown-content { background-color: #444 !important; border-color: #444 !important; }
        .dash-dropdown-actions { background-color: #222 !important; border-color: #444 !important; }
        /* 已選取的 tag */
        .dash-options-list-option { background-color: #444 !important; border-color: #555 !important; }
    </style></head>'''
)

LABEL = {"color": "#ccc", "fontSize": "12px", "fontWeight": "600",
          "marginBottom": "4px", "marginTop": "10px"}

app.layout = dbc.Container([
    html.H4("Pokémon Stat Explorer", style={"color": "white", "marginTop": "14px"}),
    dbc.Row([

        #控制面板
        dbc.Col([
            html.Div([
                html.Label("Name", style=LABEL),
                dcc.Input(
                    id='name-search', type='text', placeholder='e.g. Eevee',
                    debounce=True,
                    style={"width": "100%", "backgroundColor": "#222", "color": "white",
                        "border": "1px solid #444", "borderRadius": "4px", "padding": "5px"}
                ),

                html.Hr(style={"borderColor": "#444"}),
                html.Div(id='pokemon-card'),
                html.Hr(style={"borderColor": "#444"}),

                html.Label("Type Filter", style=LABEL),
                dcc.Dropdown(
                    id='type-filter',
                    options=[{'label': t, 'value': t} for t in all_types],
                    multi=True, placeholder="All Types...",
                ),

                html.Label("Genaration", style=LABEL),
                dbc.Checklist(
                    id='gen-filter',
                    options=[{'label': f' Gen {g}', 'value': g} for g in all_gens],
                    value=all_gens,
                    inline=False,
                    style={"color": "#ddd", "fontSize": "13px"}
                ),

                html.Label("BST Range", style=LABEL),
                dcc.RangeSlider(
                    id='bst-slider',
                    min=int(df['BST'].min()), max=int(df['BST'].max()), step=5,
                    value=[int(df['BST'].min()), int(df['BST'].max())],
                    marks={i: {"label": str(i), "style": {"color": "#aaa"}} for i in range(200, 801, 100)},
                ),

                html.Label("Extra Filter", style=LABEL),
                dbc.Checklist(
                    id='extra-filter',
                    options=[
                        {'label': 'Mega', 'value':'mega'},
                        {'label': 'Legendary', 'value':'legendary'},
                        {'label': 'Others', 'value':'others'}
                    ],
                    value=['mega','legendary','others'],
                    inline=False,
                    style={'color': '#ddd', 'fontSize': '13px'}
                ),
                
                html.Br(),
                html.Div(id='count-display',
                        style={"color": "#888", "fontSize": "12px", "textAlign": "center"}),

            ], style={'overflowY': 'auto', 'height': '85vh'}),

        ], width=3, style={"paddingRight": "10px"}),


        dbc.Col([
            dcc.Graph(id='scatter-plot', style={"height": "85vh"})
        ], width=9),

        dbc.Col([
            html.Label("Top List", style=LABEL),
            dash_table.DataTable(
                id='ranking-up',
                columns=[{'name': c, 'id': c} for c in ['Name','Type','BST','HP','Atk','Def','SpA','SpD','Spe']],
                page_size=10,
                sort_action='native',
                style_header={'backgroundColor': '#222', 'color': '#ccc', 'fontWeight': 'bold'},
                style_data={'backgroundColor': '#111', 'color': '#ddd'},
                style_cell={'border': '1px solid #333', 'textAlign': 'center'},
                style_data_conditional=[{'if': {'row_index': 0}, 'color': 'gold'}]  # 第一名金色
            )
        ], width=6, style={"marginTop": "20px"}),

        dbc.Col([
            html.Label("Bottom List", style=LABEL),
            dash_table.DataTable(
                id='ranking-down',
                columns=[{'name': c, 'id': c} for c in ['Name','Type','BST','HP','Atk','Def','SpA','SpD','Spe']],
                page_size=10,
                sort_action='native',
                style_header={'backgroundColor': '#222', 'color': '#ccc', 'fontWeight': 'bold'},
                style_data={'backgroundColor': '#111', 'color': '#ddd'},
                style_cell={'border': '1px solid #333', 'textAlign': 'center'},
                style_data_conditional=[{'if': {'row_index': 0}, 'color': 'gold'}]  # 第一名金色
            )
        ], width=6, style={"marginTop": "20px", "paddingRight": "10px"})
    ])
], fluid=True, style={"backgroundColor": "#111111"})


@callback(
    Output('scatter-plot', 'figure'),
    Output('count-display', 'children'),
    Output('ranking-up', 'data'),
    Output('ranking-down', 'data'),
    Input('type-filter', 'value'),
    Input('gen-filter', 'value'),
    Input('bst-slider', 'value'),
    Input('name-search', 'value'),
    Input('extra-filter', 'value')
)
def update_graph(selected_types, selected_gens, bst_range, name_query, special):
    filtered = df.copy()

    if selected_types:
        mask = (
            filtered['Type 1'].isin(selected_types) |
            filtered['Type 2'].isin(selected_types)
        )
        filtered = filtered[mask]

    if selected_gens:
        filtered = filtered[filtered['Generation'].isin(selected_gens)]

    if bst_range:
        filtered = filtered[
            (filtered['BST'] >= bst_range[0]) &
            (filtered['BST'] <= bst_range[1])
        ]

    if name_query:
        filtered = filtered[
            filtered['Name'].str.contains(name_query, case=False, na=False)
        ]

    # Extra Filter
    mask = pd.Series(False, index=filtered.index)
    if 'mega' in special:
        mask |= (filtered['Mega Evolution'] == 1.0)
    if 'legendary' in special:
        mask |= (filtered['Legendary'] == 1.0)
    if 'others' in special:
        mask |= (
            (filtered['Mega Evolution'] == 0.0) &
            (filtered['Legendary'] == 0.0)
        )
    filtered = filtered[mask]

    fig = px.scatter(
        filtered, x='X', y='Y',
        hover_name='Name',
        custom_data=['HP', 'Att', 'Def', 'Spa', 'Spd', 'Spe',
                     'type_display', 'BST', 'Generation', 'Height', 'Weight','Number'],
        color='Type 1',
        color_discrete_map=type_colors
    )

    fig.update_layout(
        template='plotly_dark',
        xaxis_title="◀ HP/DEF ── Speed/ATK ▶",
        yaxis_title="◀ ── BST ── ▶",
        margin=dict(l=0, r=0, t=20, b=0),
        showlegend=False
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b>  Gen %{customdata[8]}<br>"
            "Height: %{customdata[9]}m  Weight: %{customdata[10]}kg<br>"
            "Type: %{customdata[6]}<br>"
            "HP: %{customdata[0]}<br>"
            "Atk: %{customdata[1]}<br>"
            "Def: %{customdata[2]}<br>"
            "SpA: %{customdata[3]}<br>"
            "SpD: %{customdata[4]}<br>"
            "Spe: %{customdata[5]}<br>"
            "BST: <b>%{customdata[7]}</b><br>"
            "<extra></extra>"
        )
    )

    fig.update_xaxes(range=X_RANGE, autorange=False)
    fig.update_yaxes(range=Y_RANGE, autorange=False)

    top10 = (
        filtered[['Name','type_display','BST','HP','Att','Def','Spa','Spd','Spe']]
        .sort_values('BST', ascending=False)
        .head(10)
        .rename(columns={'type_display':'Type','Att':'Atk','Spa':'SpA','Spd':'SpD','Spe':'Spe'})
    )

    bottom10 = (
        filtered[['Name','type_display','BST','HP','Att','Def','Spa','Spd','Spe']]
        .sort_values('BST', ascending=True)
        .head(10)
        .rename(columns={'type_display':'Type','Att':'Atk','Spa':'SpA','Spd':'SpD','Spe':'Spe'})
    )

    count = f"Shown {len(filtered)} / {len(df)} kinds of Pokemon"
    return fig, count, top10.to_dict('records'), bottom10.to_dict('records')

@callback(Output('pokemon-card','children'), Input('scatter-plot','clickData'))
def show_card(click):
    if not click: return ""
    d = click['points'][0]
    cd = d['customdata']
    num = cd[11]
    img = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{num}.png"
    
    stats = ['Spe', 'SpD', 'SpA', 'Def', 'Atk', 'HP']
    stat_vals = [cd[5], cd[4], cd[3], cd[2], cd[1], cd[0]]
    bar = go.Figure(go.Bar(
        x=stat_vals, y=stats, orientation='h',
        marker_color='#7da6de',
        text=stat_vals,
        textposition='outside'
    ))
    bar.update_layout(
        template='plotly_dark', height=160,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(range=[0,300]),
    )
    
    return [
        html.Img(src=img, style={"width":"130px"}),
        html.P(d['hovertext'], style={"color":"white","fontWeight":"bold"}),
        html.P(f"{cd[6]}  |  BST {cd[7]}", style={"color":"#aaa","fontSize":"12px"}),
        dcc.Graph(figure=bar, config={'displayModeBar': False})
    ]

app.run(debug=True)