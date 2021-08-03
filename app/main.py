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
from plotly.subplots import make_subplots

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
    "top": 40,
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

dropdown_countries = html.Div([
    dbc.InputGroup([
        dbc.InputGroupAddon("Country"),
        dcc.Dropdown(
            id="dropdown-countries",
            options=[
                {'label': 'Spain', 'value': 'Spain'}
            ],
            value='Spain',
            style={"width": "70%"},
        ),
    ],
    )
])

dropdown_elections = html.Div([
    dbc.InputGroup([
        dbc.InputGroupAddon("Election"),
        dcc.Dropdown(
            id="dropdown-elections",
            options=[
                {'label': '2019-11-10', 'value': '2019-11-10'}
            ],
            value='2019-11-10',
            style={"width": "70%"},
        ),
    ],
    )
])

dropdown_metrics = html.Div([
    dbc.InputGroup([
        dbc.InputGroupAddon("Metrics"),
        dcc.Dropdown(
            id="dropdown-metrics",
            options=[
                #{'label': 'Seat Difference Percentage', 'value': 'Seat Difference Percentage'},
                {'label': 'Seat Difference', 'value': 'Seat Difference'},
                {'label': 'Avg. Seat Cost', 'value': 'Avg. Seat Cost'},
                {'label': 'Lost Votes Percentage', 'value': 'Lost Votes Percentage'},
            ],
            value='Seat Difference',
            style={"width": "70%"},
        ),
    ],
    )
])

system_1_card = dbc.Card(
    [
        dbc.CardHeader("System 1"),
        dbc.CardBody([
            dcc.Dropdown(
                id="dropdown-system-1",
                options=[
                    {'label': "Custom", 'value': 'Custom'},
                    {'label': "Spain", 'value': 'Spain'},
                ],
                value='Custom'
            ),
            html.Br(),
            dbc.Row([
                dbc.Col(html.P('Name'), width=4),
                dbc.Col(html.P(), width=2),
                dbc.Col(html.P('Level'), width=2),
                dbc.Col(html.P(), width=2),
                dbc.Col(html.P('Threshold (%)'), width=2),
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        id="dropdown-system-name-1",
                        # TODO Droop LR, Imperali LR, Imperiali HA, Hagenbach-Bischoff
                        options=[
                            {'label': "d'Hondt", 'value': 'dHondt'},
                            {'label': "Sainte-Laguë", 'value': 'SL'}, # https://en.wikipedia.org/wiki/Webster/Sainte-Lagu%C3%AB_method
                            {'label': "Modified Sainte-Laguë", 'value': 'MSL'}, # https://en.wikipedia.org/wiki/Webster/Sainte-Lagu%C3%AB_method
                            {'label': "LRM (Hare Quota)", 'value': 'LRM-Hare'}, # https://en.wikipedia.org/wiki/Largest_remainder_method
                            {'label': "LRM (Droop Quota)", 'value': 'LRM-Droop'},
                            {'label': "LRM (Hagenbach-Bischoff Quota)", 'value': 'LRM-HB'},
                            {'label': "LRM (Imperiali Quota)", 'value': 'LRM-Imperiali'},
                        ],
                        value='dHondt'
                    ),
                    width=4
                ),
                dbc.Col(html.P(), width=2),
                dbc.Col(
                    dcc.Dropdown(
                        id="dropdown-region-level-1",
                        options=[
                            {'label': '0', 'value': '0'},
                            {'label': '1', 'value': '1'},
                            {'label': '2', 'value': '2'},
                        ],
                        value='2'
                    ),
                    width=2
                ),
                dbc.Col(html.P(), width=2),
                dbc.Col(
                    dcc.Input(
                        id="threshold-1",
                        type="number",
                        min=0, max=15, step=1,
                        value=3
                    ),
                    width=2
                ),
            ])
        ]),
    ],
)

system_2_card = dbc.Card(
    [
        dbc.CardHeader("System 2"),
        dbc.CardBody([
            dcc.Dropdown(
                id="dropdown-system-2",
                options=[
                    {'label': "Custom", 'value': 'Custom'},
                    {'label': "Spain", 'value': 'Spain'},
                ],
                value='Custom'
            ),
            html.Br(),
            dbc.Row([
                dbc.Col(html.P('Name'), width=4),
                dbc.Col(html.P(), width=2),
                dbc.Col(html.P('Level'), width=2),
                dbc.Col(html.P(), width=2),
                dbc.Col(html.P('Threshold (%)'), width=2),
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        id="dropdown-system-name-2",
                        options=[
                            {'label': "d'Hondt", 'value': 'dHondt'},
                            {'label': "Sainte-Laguë", 'value': 'SL'}, # https://en.wikipedia.org/wiki/Webster/Sainte-Lagu%C3%AB_method
                            {'label': "Modified Sainte-Laguë", 'value': 'MSL'}, # https://en.wikipedia.org/wiki/Webster/Sainte-Lagu%C3%AB_method
                            {'label': "LRM (Hare Quota)", 'value': 'LRM-Hare'}, # https://en.wikipedia.org/wiki/Largest_remainder_method
                            {'label': "LRM (Droop Quota)", 'value': 'LRM-Droop'},
                            {'label': "LRM (Hagenbach-Bischoff Quota)", 'value': 'LRM-HB'},
                            {'label': "LRM (Imperiali Quota)", 'value': 'LRM-Imperiali'},
                        ],
                        value='dHondt'
                    ),
                    width=4
                ),
                dbc.Col(html.P(), width=2),
                dbc.Col(
                    dcc.Dropdown(
                        id="dropdown-region-level-2",
                        options=[
                            {'label': '0', 'value': '0'},
                            {'label': '1', 'value': '1'},
                            {'label': '2', 'value': '2'},
                        ],
                        value='2'
                    ),
                    width=2
                ),
                dbc.Col(html.P(), width=2),
                dbc.Col(
                    dcc.Input(
                        id="threshold-2",
                        type="number",
                        min=0, max=15, step=1,
                        value=3
                    ),
                    width=2
                ),
            ])
        ]),
    ],
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
    color='primary',
    outline=True,
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
    color='primary',
    outline=True,
)

content2 = html.Div([
    dbc.Row([
        dbc.Col(dropdown_countries, width=3),
        dbc.Col(html.P(), width=1),
        dbc.Col(dropdown_elections, width=3),
        dbc.Col(html.P(), width=1),
        dbc.Col(dropdown_metrics, width=3),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(system_1_card, width=6),
        dbc.Col(system_2_card, width=6),
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
        dbc.Col(dcc.Graph(id='chart'), width=5),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(dcc.Graph(id='pie-1'), width=7),
        dbc.Col(dcc.Graph(id='pie-2'), width=5),
    ]),
    ],
    style=CONTENT_STYLE
)


app.layout = html.Div([
    content2
])

print("Everything is loaded!")

#######################
###### CALLBACKS ######
#######################

# Make this callback on the client side?
@app.callback([Output('dropdown-elections', 'options'),
               Output('dropdown-elections', 'value')],
              Input('dropdown-countries', 'value'))
def update_dropdown_elections(country):
    if country=='Spain':
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
        value = '2019-11-10'
    return options, value

@app.callback([
        Output('dropdown-system-name-1', 'value'),
        Output('dropdown-region-level-1', 'value'),
        Output('threshold-1', 'value'),
    ],
    Input('dropdown-system-1', 'value'),
    [
        State('dropdown-system-name-1', 'value'),
        State('dropdown-region-level-1', 'value'),
        State('threshold-1', 'value'),
    ])
def set_system_1(system_1, s1_name, s1_level, s1_threshold):
    if system_1=='Spain':
        s1_name = 'dHondt'
        s1_level = 2
        s1_threshold = 3
    return s1_name, s1_level, s1_threshold

@app.callback([
        Output('dropdown-system-name-2', 'value'),
        Output('dropdown-region-level-2', 'value'),
        Output('threshold-2', 'value'),
    ],
    Input('dropdown-system-2', 'value'),
    [
        State('dropdown-system-name-2', 'value'),
        State('dropdown-region-level-2', 'value'),
        State('threshold-2', 'value'),
    ])
def set_system_2(system_2, s2_name, s2_level, s2_threshold):
    if system_2=='Spain':
        s2_name = 'dHondt'
        s2_level = 2
        s2_threshold = 3
    return s2_name, s2_level, s2_threshold

@app.callback([
        Output('map', 'figure'),
        Output('chart', 'figure'),
        Output('pie-1', 'figure'),
        Output('dropdown-system-2', 'disabled'),
        Output('dropdown-system-name-2', 'disabled'),
        Output('dropdown-region-level-2', 'disabled'),
        Output('threshold-2', 'disabled'),
        Output('card-1-header', 'children'),
        Output('card-1-title', 'children'),
        Output('card-2-header', 'children'),
        Output('card-2-title', 'children'),
    ],
    [
        Input("dropdown-metrics", "value"),
        Input('dropdown-system-name-1', 'value'),
        Input('dropdown-region-level-1', 'value'),
        Input('threshold-1', 'value'),
        Input('dropdown-system-name-2', 'value'),
        Input('dropdown-region-level-2', 'value'),
        Input('threshold-2', 'value'),
        Input('dropdown-elections', 'value'),
    ],
    [
        State('dropdown-countries', 'value'),
    ])
def update_maps(metric, system_1, level_1, threshold_1, system_2, level_2, threshold_2, elections, country):

    election = ELECTIONS[country][elections]

    regions = election.regions()

    if metric.startswith('Seat Difference'):
        disable = False

        level_1, level_2 = int(level_1), int(level_2)
        level = min(level_1, level_2)
        locations = [region.name for region in regions[level]]

        s1 = {'name': system_1, 'threshold': threshold_1, 'level': level_1}
        s2 = {'name': system_2, 'threshold': threshold_2, 'level': level_2}
        metrics = election.get_compare_metrics(s1, s2)

        seat_diff = list(metrics['seat_diff'].values())
        map_fig = go.Figure(go.Choroplethmapbox(geojson=election.country.regions()[level]['geojson'],
                                                locations=locations,
                                                z=seat_diff,
                                                #colorbar={'title': metric},
                                                colorscale="Reds", # Options: Greys,YlGnBu,Greens,YlOrR d,Bluered,RdBu,Reds,Blues,Picnic,Rainbow,Portland,Jet,H ot,Blackbody,Earth,Electric,Viridis,Cividis.
                                                zmin=0, zmax=max(10, max(seat_diff)),
                                                marker_line_width=0))
        #map_fig.update_layout(title=metric)

        seats_won = {k:v for k,v in metrics['seats_won'].items() if v != 0}
        seats_won = dict(sorted(seats_won.items(), key=lambda item: item[1], reverse=True))
        bar_colors = [election.colors[k] for k in seats_won.keys()]
        bar_fig = go.Figure(data=[go.Bar(
            x = [k for k in seats_won.keys()],
            y = [v for v in seats_won.values()],
            marker_color = bar_colors,
        )])
        bar_fig.update_layout(
            title_text='Total Seats Won/Lost',
            yaxis=dict(
                title='Seats Sys 1 - Seats Sys 2',
                titlefont_size=16,
                tickfont_size=14,
            ),
        )

        card_1_header = 'Total Seat Difference'
        card_1_title = str(sum(seat_diff)) + '/' + str(regions[0][0].n_seats)
        card_2_header = 'Seat Difference Percentage'
        card_2_title = "{:.2f}%".format(100 * (sum(seat_diff)) / regions[0][0].n_seats)

        # Pie charts
        final_results_1 = metrics['final_results_1']
        final_results_2 = metrics['final_results_2']
        labels = list(set(final_results_1.keys()).union(set(final_results_2.keys())))
        colors = [election.colors[x] for x in labels]
        # Create subplots: use 'domain' type for Pie subplot
        pie = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
        pie.add_trace(go.Pie(labels=labels, values=[final_results_1[x] if x in final_results_1 else 0 for x in labels],
                             name="System 1", marker_colors=colors),
                      1, 1)
        pie.add_trace(go.Pie(labels=labels, values=[final_results_2[x] if x in final_results_2 else 0 for x in labels],
                             name="System 2", marker_colors=colors),
                      1, 2)
        # Use `hole` to create a donut-like pie chart
        pie.update_traces(hole=.4, hoverinfo="label+percent+name", textinfo='value', textfont_size=20, textposition='inside')
        pie.update_layout(
            title_text="Final results",
            uniformtext_minsize=12,
            uniformtext_mode='hide',
            # Add annotations in the center of the donut pies.
            annotations=[dict(text='1', x=0.21, y=0.5, font_size=20, showarrow=False),
                         dict(text='2', x=0.79, y=0.5, font_size=20, showarrow=False)]),

    else:
        disable = True

        level = int(level_1)
        locations = [region.name for region in regions[level]]

        s1 = {'name': system_1, 'threshold': threshold_1, 'level': level}
        metrics = election.get_single_metrics(s1)

        lost_votes_percentage = list(metrics['lost_votes_percentage'].values())
        map_fig = go.Figure(go.Choroplethmapbox(geojson=election.country.regions()[level]['geojson'],
                                                locations=locations,
                                                z=lost_votes_percentage,
                                                colorscale="Reds",
                                                zmin=0, zmax=1,
                                                marker_line_width=0))

        party_lost_votes = metrics['party_lost_votes']
        total_lost_votes = sum(party_lost_votes.values())
        party_lost_votes = party_lost_votes.most_common(10)
        bar_colors = [election.colors[x[0]] if x[0] in election.colors else '#7D7D7D' for x in party_lost_votes]
        bar_fig = go.Figure(data=[go.Bar(
            x = [x[0] for x in party_lost_votes],
            y = [x[1] for x in party_lost_votes],
            marker_color = bar_colors,
        )])
        bar_fig.update_layout(
            title_text='Lost votes per party',
            yaxis=dict(
                title='Lost Votes',
                titlefont_size=16,
                tickfont_size=14,
            ),
        )


        total_votes = sum(regions[0][0].votes.values())

        card_1_header = 'Total % of Lost Votes'
        card_1_title = "{:.2f}%".format(100 * total_lost_votes / total_votes)
        card_2_header = 'Total Lost Votes'
        card_2_title = str(total_lost_votes)

        pie = {}
        # Pie charts
        final_results_1 = metrics['final_results']
        labels = list(final_results_1.keys())
        colors = [election.colors[x] for x in labels]
        # Create subplots: use 'domain' type for Pie subplot
        pie = make_subplots(rows=1, cols=1, specs=[[{'type':'domain'}]])
        pie.add_trace(go.Pie(labels=labels, values=[final_results_1[x] if x in final_results_1 else 0 for x in labels],
                             name="System 1", marker_colors=colors),
                      1, 1)
        # Use `hole` to create a donut-like pie chart
        pie.update_traces(hole=.4, hoverinfo="label+percent+name", textinfo='value', textfont_size=20, textposition='inside')
        pie.update_layout(
            title_text="Final results",
            uniformtext_minsize=12,
            uniformtext_mode='hide',
        ),


    map_fig.update_layout(mapbox_style="light",
                          mapbox_accesstoken=MAPBOX_ACCESS_TOKEN,
                          mapbox_zoom=election.country.zoom(),
                          mapbox_center = election.country.center(),
                          margin={"r":0,"t":0,"l":0,"b":0})

    return map_fig, bar_fig, pie, disable, disable, disable, disable, card_1_header, card_1_title, card_2_header, card_2_title


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True, port=800)
