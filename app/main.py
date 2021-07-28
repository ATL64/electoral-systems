from collections import Counter
import dash
from dash.dependencies import Input, Output, State, ALL
import dash_auth
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash_extensions.javascript import arrow_function
import dash_html_components as html
import dash_table
import geopandas as gpd
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
#from plotly.subplots import make_subplots

# Custom modules
import Election

# initialize all the elections so that all the data loading is done when starting the app
ELECTIONS = {
    'Spain': {
        '2019-11-10': Election.Spain_2019_11(),
        '2019-04-28': Election.Spain_2019_04(),
        '2016-06-26': Election.Spain_2016_06(),
        '2015-12-20': Election.Spain_2015_12(),
        '2011-11-20': Election.Spain_2011_11(),
        '2008-03-09': Election.Spain_2008_03(),
        '2004-03-14': Election.Spain_2004_03(),
        '2000-03-12': Election.Spain_2000_03(),
    }
}

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN])

MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoiYWRlbWlxdWVsIiwiYSI6ImNrcmFiMWxpdTRoZm0ydm1mb3FieHBueHIifQ.8Vz0HX4TMOQN1ywDSEPtSw"
MAPBOX_STYLE = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

##############
### LAYOUT ###
##############

CONTENT_STYLE = {
    "position": "relative",
    "top": 60,
    "bottom": 0,
    "left": 0,
    "right": 0,
    "margin-top": 25,
    "margin-left": "5rem",
    "margin-right": "5rem",
    "margin-bottom": 100,
    #"padding": "2rem 1rem",
    "zIndex": 80
}

dropdown_countries = dcc.Dropdown(
    id="dropdown-countries",
    options=[
        {'label': 'Spain', 'value': 'Spain'}
    ],
    value='Spain'
)

dropdown_elections = dcc.Dropdown(
    id="dropdown-elections",
    options=[
        {'label': '2019-11-10', 'value': '2019-11-10'}
    ],
    value='2019-11-10'
)

compare_switch = dbc.Checklist(
    options=[{"label": "Compare", "value": 1}],
    value=[1],
    id="switch-compare",
    switch=True
)

dropdown_system_1 = dcc.Dropdown(
    id="dropdown-system-1",
    options=[
        {'label': "d'Hondt", 'value': 'dHondt'},
        {'label': "Sainte-Laguë", 'value': 'SL'},
    ],
    value='dHondt'
)

dropdown_system_2 = dcc.Dropdown(
    id="dropdown-system-2",
    options=[
        {'label': "d'Hondt", 'value': 'dHondt'},
        {'label': "Sainte-Laguë", 'value': 'SL'},
    ],
    value='SL'
)

dropdown_region_level_1 = dcc.Dropdown(
    id="dropdown-region-level-1",
    options=[
        {'label': '0', 'value': '0'},
        {'label': '1', 'value': '1'},
        {'label': '2', 'value': '2'},
    ],
    value='2'
)

dropdown_region_level_2 = dcc.Dropdown(
    id="dropdown-region-level-2",
    options=[
        {'label': '0', 'value': '0'},
        {'label': '1', 'value': '1'},
        {'label': '2', 'value': '2'},
    ],
    value='2'
)

threshold_1 = dcc.Input(
    id="threshold-1",
    type="number",
    min=0, max=15, step=1,
    value=3
)

threshold_2 = dcc.Input(
    id="threshold-2",
    type="number",
    min=0, max=15, step=1,
    value=3
)

info_box_1 = dbc.Card(
    [
        dbc.CardHeader("", id='card-1-header'),
        dbc.CardBody(
            [
                html.H4("", id="card-1-title"),
            ]
        ),
    ],
    style={"width": "18rem"},
)

info_box_2 = dbc.Card(
    [
        dbc.CardHeader("", id='card-2-header'),
        dbc.CardBody(
            [
                html.H4("", id="card-2-title"),
            ]
        ),
    ],
    style={"width": "18rem"},
)

content = html.Div([
        dbc.Row([
            dbc.Col(dropdown_countries, width=2),
            dbc.Col(dropdown_elections, width=2),
            dbc.Col(compare_switch, width=8),
        ]),
        dbc.Row([
            dbc.Col(html.P(), width=4),
            dbc.Col(dropdown_system_1, width=2),
            dbc.Col(dropdown_system_2, width=2),
        ]),
        dbc.Row([
            dbc.Col(html.P(), width=4),
            dbc.Col(dropdown_region_level_1, width=2),
            dbc.Col(dropdown_region_level_2, width=2),
        ]),
        dbc.Row([
            dbc.Col(html.P(), width=4),
            dbc.Col(threshold_1, width=2),
            dbc.Col(threshold_2, width=2),
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(html.P(), width=1),
            dbc.Col(info_box_1, width=4),
            dbc.Col(html.P(), width=2),
            dbc.Col(info_box_2, width=4),
            dbc.Col(html.P(), width=1),
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(dcc.Graph(id='map'), width=7),
            dbc.Col(dcc.Graph(id='chart'), width=5)
        ]),
    ],
    style=CONTENT_STYLE
)


app.layout = html.Div([
    content
])

print("Everything is loaded!")

#######################
###### CALLBACKS ######
#######################

# Make this callback on the client side?
@app.callback(Output('dropdown-elections', 'options'),
              Input('dropdown-countries', 'value'))
def update_dropdown_elections(country):
    options=[
        {'label': '2019-11-10', 'value': '2019-11-10'},
        {'label': '2019-04-28', 'value': '2019-04-28'},
        {'label': '2016-06-26', 'value': '2016-06-26'},
        {'label': '2015-12-20', 'value': '2015-12-20'},
        {'label': '2011-11-20', 'value': '2011-11-20'},
        {'label': '2008-03-09', 'value': '2008-03-09'},
        {'label': '2004-03-14', 'value': '2004-03-14'},
        {'label': '2000-03-12', 'value': '2000-03-12'},
    ]
    return options

@app.callback([
        Output('dropdown-system-1', 'value'),
        Output('dropdown-region-level-1', 'value'),
        Output('threshold-1', 'value'),
        Output('dropdown-system-2', 'value'),
        Output('dropdown-region-level-2', 'value'),
        Output('threshold-2', 'value'),
    ],
    Input('dropdown-elections', 'value'),
    State('dropdown-countries', 'value'))
def set_default_election_values(elections, country):
    election = ELECTIONS[country][elections]
    system = election.electoral_system()
    return system['name'], system['level'], system['threshold']*100, system['name'], system['level'], system['threshold']*100

@app.callback([
        Output("map", "figure"),
        Output("chart", "figure"),
        Output('dropdown-system-2', 'disabled'),
        Output('dropdown-region-level-2', 'disabled'),
        Output('threshold-2', 'disabled'),
        Output('card-1-header', 'children'),
        Output('card-1-title', 'children'),
        Output('card-2-header', 'children'),
        Output('card-2-title', 'children'),
    ],
    [
        Input("switch-compare", "value"),
        Input('dropdown-system-1', 'value'),
        Input('dropdown-region-level-1', 'value'),
        Input('threshold-1', 'value'),
        Input('dropdown-system-2', 'value'),
        Input('dropdown-region-level-2', 'value'),
        Input('threshold-2', 'value'),
    ],
    [
        State('dropdown-countries', 'value'),
        State('dropdown-elections', 'value'),
    ])
def update_maps(compare, system_1, level_1, threshold_1, system_2, level_2, threshold_2, country, elections):
    level_1, level_2 = int(level_1), int(level_2)

    election = ELECTIONS[country][elections]

    regions = election.regions()
    locations = [region.name for region in regions[level_1]]

    if compare:
        disable = False

        s1 = {'name': system_1, 'threshold': threshold_1, 'level': level_1}
        s2 = {'name': system_2, 'threshold': threshold_2, 'level': level_2}
        metrics = election.get_compare_metrics(s1, s2)

        seat_diff = list(metrics['seat_diff'].values())
        map_fig = go.Figure(go.Choroplethmapbox(geojson=election.country.regions()[level_1]['geojson'],
                                                locations=locations,
                                                z=seat_diff,
                                                colorscale="Reds", # Options: Greys,YlGnBu,Greens,YlOrR d,Bluered,RdBu,Reds,Blues,Picnic,Rainbow,Portland,Jet,H ot,Blackbody,Earth,Electric,Viridis,Cividis.
                                                zmin=0, zmax=max(seat_diff),
                                                marker_line_width=0))

        seats_won = {k:v for k,v in metrics['seats_won'].items() if v != 0}
        bar_fig = {'parties': [k for k in seats_won.keys()], 'seats_won': [v for v in seats_won.values()]}
        bar_fig = px.bar(bar_fig, x='parties', y='seats_won')

        card_1_header = 'Total Seat Difference'
        card_1_title = str(sum(seat_diff)  // 2) + '/' + str(regions[0][0].n_seats)
        card_2_header = 'Seat Difference Percentage'
        card_2_title = "{:.2f}%".format(100 * (sum(seat_diff)  // 2) / regions[0][0].n_seats)

    else:
        disable = True

        s1 = {'name': system_1, 'threshold': threshold_1, 'level': level_1}
        metrics = election.get_single_metrics(s1)

        lost_votes_percentage = list(metrics['lost_votes_percentage'].values())
        map_fig = go.Figure(go.Choroplethmapbox(geojson=election.country.regions()[level_1]['geojson'],
                                                locations=locations,
                                                z=lost_votes_percentage,
                                                colorscale="Reds",
                                                zmin=0, zmax=1,
                                                marker_line_width=0))

        party_lost_votes = metrics['party_lost_votes']
        total_lost_votes = sum(party_lost_votes.values())
        party_lost_votes = party_lost_votes.most_common(10)
        bar_fig = {'parties': [x[0] for x in party_lost_votes], 'lost_votes': [x[1] for x in party_lost_votes]}
        bar_fig = px.bar(bar_fig, x='parties', y='lost_votes')

        total_votes = sum(regions[0][0].votes.values())

        card_1_header = 'Total % of Lost Votes'
        card_1_title = "{:.2f}%".format(100 * total_lost_votes / total_votes)
        card_2_header = 'Total Lost Votes'
        card_2_title = str(total_lost_votes)


    map_fig.update_layout(mapbox_style="light",
                          mapbox_accesstoken=MAPBOX_ACCESS_TOKEN,
                          mapbox_zoom=election.country.zoom(),
                          mapbox_center = election.country.center(),
                          margin={"r":0,"t":0,"l":0,"b":0})

    return map_fig, bar_fig, disable, disable, disable, card_1_header, card_1_title, card_2_header, card_2_title


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True, port=800)