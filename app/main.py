from collections import Counter
import dash
from dash.dependencies import Input, Output, State, ALL
import dash_auth
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash_daq import BooleanSwitch
from dash_extensions.javascript import arrow_function
import dash_html_components as html
import dash_table
import geopandas as gpd
import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Custom modules
import Election

with open('texts/about.md', 'r') as file:
    about_md = file.read()
with open('texts/country_election_metric.md', 'r') as file:
    country_md = file.read()
with open('texts/electoral_systems.md', 'r') as file:
    systems_md = file.read()

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
    "zIndex": 80
}

system_unselected_color = '#F4CCCC'

dropdown_countries = dcc.Dropdown(
    id="dropdown-countries",
    options=[
        {'label': 'Spain', 'value': 'Spain'}
    ],
    value='Spain',
    placeholder='Country',
    style={'font-size': '20px'},
    clearable=False,
)

dropdown_elections = dcc.Dropdown(
    id="dropdown-elections",
    options=[
        {'label': '2019-11-10', 'value': '2019-11-10'}
    ],
    value='2019-11-10',
    placeholder='Election',
    style={'font-size': '20px', 'margin-top': '5px'},
    clearable=False,
)

dropdown_metrics = dcc.Dropdown(
    id="dropdown-metrics",
    options=[
        {'label': 'Seat Difference', 'value': 'Seat Difference'},
        #{'label': 'Avg. Seat Cost', 'value': 'Avg. Seat Cost'},
        {'label': 'Lost Votes', 'value': 'Lost Votes'},
    ],
    value='Seat Difference',
    placeholder='Metric',
    style={'font-size': '20px', 'margin-top': '5px'},
    clearable=False,
)

## BUTTONS
about_button = html.Div(
    [
        dbc.Button("About", id="about-button", n_clicks=0, size='lg', color='primary'),
        dbc.Modal([dbc.ModalBody(dcc.Markdown(about_md))],
            id="about-modal",
            is_open=False,
            size='lg',
            scrollable=True,
            style={'font-size': '20px'}
        ),
    ],
    style={'justify-content': 'flex-end', 'display': 'flex'}
)

countries_button = html.Div(
    [
        dbc.Button("?", id="countries-button", n_clicks=0, color='primary'),
        dbc.Modal([dbc.ModalBody(dcc.Markdown(country_md))],
            id="countries-modal",
            is_open=False,
            size='lg',
            scrollable=True,
            style={'font-size': '20px'}
        ),
    ],
    style={'justify-content': 'flex-end', 'display': 'flex'}
)

systems_button = html.Div(
    [
        dbc.Button("?", id="systems-button", n_clicks=0, color='primary'),
        dbc.Modal([dbc.ModalBody(dcc.Markdown(systems_md))],
            id="systems-modal",
            is_open=False,
            size='lg',
            scrollable=True,
            style={'font-size': '20px'}
        ),
    ],
    style={'justify-content': 'flex-end', 'display': 'flex'}
)

system_1_dropdown = dcc.Dropdown(
    id="dropdown-system-name-1",
    # TODO Droop LR, Imperali LR, Imperiali HA, Hagenbach-Bischoff
    options=[
        {'label': "d'Hondt", 'value': 'dHondt'},
        {'label': "Sainte-Laguë", 'value': 'SL'}, # https://en.wikipedia.org/wiki/Webster/Sainte-Lagu%C3%AB_method
        #{'label': "Modified Sainte-Laguë", 'value': 'MSL'}, # https://en.wikipedia.org/wiki/Webster/Sainte-Lagu%C3%AB_method
        {'label': "LRM (Hare Quota)", 'value': 'LRM-Hare'}, # https://en.wikipedia.org/wiki/Largest_remainder_method
        {'label': "LRM (Droop Quota)", 'value': 'LRM-Droop'},
        {'label': "LRM (Hagenbach-Bischoff Quota)", 'value': 'LRM-HB'},
        {'label': "LRM (Imperiali Quota)", 'value': 'LRM-Imperiali'},
    ],
    placeholder='System 1',
    value='dHondt',
    style={'font-size': '20px'},
    clearable=False,
)

system_1_levels = dcc.Dropdown(
    id="dropdown-region-level-1",
    options=[
        {'label': '0: Country', 'value': 0},
        {'label': '1: Aut. Community', 'value': 1},
        {'label': '2: Province', 'value': 2},
    ],
    placeholder='Level',
    value=2,
    style={'font-size': '20px', 'margin-top': '5px'},
    clearable=False,
)

system_1_threshold = dbc.Row([
    dbc.Col(
        dcc.Dropdown(
            id="threshold-1",
            options=[{'label': str(x)+'%', 'value': x} for x in range(16)],
            placeholder='Threshold',
            value=3,
            style={'font-size': '20px', 'margin-top': '5px'},
            clearable=False,
            ),
        width=5
    ),
    dbc.Col(
        BooleanSwitch(
            id='threshold-switch-1',
            on=False,
            label={'label': "Country", 'style': {'font-size': '20px', 'margin-top': '5px'}},
            labelPosition="left",
            style={'font-size': '20px', 'margin-top': '5px'},
        ),
        width=7
    )
])

system_1_group = html.Div([
    dbc.Row([
        dbc.Col(html.P('System 1', style={'font-size': '20px'}), width=10),
        dbc.Col(systems_button, width=2)
    ]),
    system_1_dropdown,
    system_1_levels,
    system_1_threshold,
])

system_2_dropdown = dcc.Dropdown(
    id="dropdown-system-name-2",
    # TODO Droop LR, Imperali LR, Imperiali HA, Hagenbach-Bischoff
    options=[
        {'label': "d'Hondt", 'value': 'dHondt'},
        {'label': "Sainte-Laguë", 'value': 'SL'}, # https://en.wikipedia.org/wiki/Webster/Sainte-Lagu%C3%AB_method
        #{'label': "Modified Sainte-Laguë", 'value': 'MSL'}, # https://en.wikipedia.org/wiki/Webster/Sainte-Lagu%C3%AB_method
        {'label': "LRM (Hare Quota)", 'value': 'LRM-Hare'}, # https://en.wikipedia.org/wiki/Largest_remainder_method
        {'label': "LRM (Droop Quota)", 'value': 'LRM-Droop'},
        {'label': "LRM (Hagenbach-Bischoff Quota)", 'value': 'LRM-HB'},
        {'label': "LRM (Imperiali Quota)", 'value': 'LRM-Imperiali'},
    ],
    placeholder='System 2',
    value='SL',
    style={'font-size': '20px'},
    clearable=False,
)

system_2_levels = dcc.Dropdown(
    id="dropdown-region-level-2",
    options=[
        {'label': '0: Country', 'value': 0},
        {'label': '1: Aut. Community', 'value': 1},
        {'label': '2: Province', 'value': 2},
    ],
    placeholder='Level',
    value=2,
    style={'font-size': '20px', 'margin-top': '5px'},
    clearable=False,
)

system_2_threshold = dbc.Row([
    dbc.Col(
        dcc.Dropdown(
            id="threshold-2",
            options=[{'label': str(x)+'%', 'value': x} for x in range(16)],
            placeholder='Threshold',
            value=3,
            style={'font-size': '20px', 'margin-top': '5px'},
            clearable=False,
            ),
        width=5
    ),
    dbc.Col(
        BooleanSwitch(
            id='threshold-switch-2',
            on=False,
            label={'label': "Country", 'style': {'font-size': '20px', 'margin-top': '5px'}},
            labelPosition="left",
            style={'font-size': '20px', 'margin-top': '5px'},
        ),
        width=7
    )
])

system_2_group = html.Div([
    html.P('System 2', style={'font-size': '20px'}),
    system_2_dropdown,
    system_2_levels,
    system_2_threshold,
])

## GRAPHS
graphs = dbc.Row([
    dbc.Col(html.Div([
            dcc.Graph(id='chart'),
            dcc.Graph(id='pie-1'),
        ]),
        width=7,
    ),
    dbc.Col(dcc.Graph(id='map'), width=5),
])

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "22rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H3("Comparing Electoral Systems"),
        html.Hr(),
        dbc.Row([dbc.Col(html.P("Select country, election date and metric to be displayed", className="lead"), width=10),
                 dbc.Col(countries_button, width=2)
        ]),
        dropdown_countries,
        dropdown_elections,
        dropdown_metrics,
        html.Hr(),
        system_1_group,
        html.Br(),
        system_2_group,
        html.Hr(),
        html.H3("", id='extra-text-title'),
        html.P("", id='extra-text', style={'font-size': '25px'}),
        about_button,
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(graphs, style=CONTENT_STYLE)

app.layout = html.Div([
    sidebar,
    content
])

print("Everything is loaded!")

#######################
###### CALLBACKS ######
#######################

# Make this callback on the client side?
@app.callback(
    [Output('dropdown-elections', 'options'),
    Output('dropdown-elections', 'value'),
    Output('dropdown-region-level-1', 'options'),
    Output('dropdown-region-level-1', 'value'),
    Output('dropdown-region-level-2', 'options'),
    Output('dropdown-region-level-2', 'value'),
    ],
    Input('dropdown-countries', 'value'))
def switch_country(country):
    if country=='Spain':
        election_options=[
            {'label': '2019-11-10', 'value': '2019-11-10'},
            {'label': '2019-04-28', 'value': '2019-04-28'},
            {'label': '2016-06-26', 'value': '2016-06-26'},
            {'label': '2015-12-20', 'value': '2015-12-20'},
            {'label': '2011-11-20', 'value': '2011-11-20'},
            {'label': '2008-03-09', 'value': '2008-03-09'},
            {'label': '2004-03-14', 'value': '2004-03-14'},
            {'label': '2000-03-12', 'value': '2000-03-12'},
        ]
        election_value = '2019-11-10'

        level_options=[
            {'label': '0: Country', 'value': 0},
            {'label': '1: Aut. Community', 'value': 1},
            {'label': '2: Province', 'value': 2},
        ]
        level_value = 2
    return election_options, election_value, level_options, level_value, level_options, level_value

@app.callback(
    Output("about-modal", "is_open"),
    [Input("about-button", "n_clicks")],
    [State("about-modal", "is_open")],
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

@app.callback(
    Output("countries-modal", "is_open"),
    [Input("countries-button", "n_clicks")],
    [State("countries-modal", "is_open")],
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

@app.callback(
    Output("systems-modal", "is_open"),
    [Input("systems-button", "n_clicks")],
    [State("systems-modal", "is_open")],
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

@app.callback([
        Output('map', 'figure'),
        Output('chart', 'figure'),
        Output('pie-1', 'figure'),
        Output('dropdown-system-name-2', 'disabled'),
        Output('dropdown-region-level-2', 'disabled'),
        Output('threshold-2', 'disabled'),
        Output('dropdown-system-name-2', 'style'),
        Output('dropdown-region-level-2', 'style'),
        Output('threshold-2', 'style'),
    ],
    [
        Input("dropdown-metrics", "value"),
        Input('dropdown-system-name-1', 'value'),
        Input('dropdown-region-level-1', 'value'),
        Input('threshold-1', 'value'),
        Input('threshold-switch-1', 'on'),
        Input('dropdown-system-name-2', 'value'),
        Input('dropdown-region-level-2', 'value'),
        Input('threshold-2', 'value'),
        Input('threshold-switch-2', 'on'),
        Input('dropdown-elections', 'value'),
    ],
    [
        State('dropdown-countries', 'value'),
    ])
def update_maps(metric, system_1, level_1, threshold_1, threshold_1_country, system_2, level_2, threshold_2, threshold_2_country, elections, country):
    election = ELECTIONS[country][elections]

    regions = election.regions()

    level = min(level_1, level_2)
    locations = [region.name for region in regions[level]]

    s1 = {'name': system_1, 'level': level_1, 'threshold': threshold_1, 'threshold_country': threshold_1_country}
    s2 = {'name': system_2, 'level': level_2, 'threshold': threshold_2, 'threshold_country': threshold_2_country}

    if metric.startswith('Seat Difference'):
        disable = False
        dropdown_style={'font-size': '20px', 'margin-top': '5px'}

        metrics = election.get_compare_metrics(s1, s2)

        final_results_1 = Counter()
        final_results_2 = Counter()
        for region in regions[level]:
            final_results_1 += metrics['results_1'][region.name]
        for region in regions[level]:
            final_results_2 += metrics['results_2'][region.name]

        hover_strings = []
        for r in locations:
            hover_string = f"{sum(metrics['results_1'][r].values())} seats <br><br>"
            region_parties = [key for key,value in sorted(metrics['results_1'][r].items(), key=lambda x : x[1], reverse=True)]
            for k in metrics['results_2'][r]:
                if k not in metrics['results_1'][r]:
                    region_parties.append(k)
            #region_parties = list(set(metrics['results_1'][r].keys()).union(set(metrics['results_2'][r].keys())))
            for p in region_parties:
                hover_string += f"{p} \t"
                if p in metrics['results_1'][r]:
                    hover_string += f"{metrics['results_1'][r][p]} \t"
                else:
                    hover_string += "0 \t"
                if p in metrics['results_2'][r]:
                    hover_string += f"{metrics['results_2'][r][p]} <br>"
                else:
                    hover_string += "0 <br>"
            hover_string += f"<extra>{r}</extra>"
            hover_strings.append(hover_string)

        seat_diff = list(metrics['seat_diff'].values())

        map_fig = go.Figure(go.Choroplethmapbox(
            geojson=election.country.regions()[level]['geojson'],
            locations=locations,
            z=seat_diff,
            colorscale="Reds", # Options: Greys,YlGnBu,Greens,YlOrR d,Bluered,RdBu,Reds,Blues,Picnic,Rainbow,Portland,Jet,H ot,Blackbody,Earth,Electric,Viridis,Cividis.
            zmin=0, zmax=max(10, max(seat_diff)),
            marker_line_width=1,
            customdata = hover_strings,
            hovertemplate = '%{customdata}',
            ),
        )
        map_fig.update_layout(title='Seat difference per Region')

        seats_won = {k:v for k,v in metrics['seats_won'].items() if v != 0}
        seats_won = dict(sorted(seats_won.items(), key=lambda item: item[1], reverse=True))
        bar_colors = [election.colors[k] for k in seats_won.keys()]
        bar_fig = go.Figure(data=[go.Bar(
            x = [k for k in seats_won.keys()],
            y = [v for v in seats_won.values()],
            marker_color = bar_colors,
        )])
        bar_title = 'Total Seats Won/Lost\t (TotalSeat Difference: {}/{} -- {:.2f}%)'.format(sum(seat_diff), regions[0][0].n_seats, 100 * (sum(seat_diff)) / regions[0][0].n_seats)
        bar_fig.update_layout(
            #title='Total Seats Won/Lost',
            title=bar_title,
            yaxis=dict(
                title='Seats Sys 1 - Seats Sys 2',
                titlefont_size=16,
                tickfont_size=14,
            ),
        )
        bar_fig.update_layout(margin=dict(t=40, b=20, l=0, r=0))

        card_1_header = 'Total Seat Difference'
        card_1_title = str(sum(seat_diff)) + '/' + str(regions[0][0].n_seats)
        card_2_header = 'Seat Difference Percentage'
        card_2_title = "{:.2f}%".format(100 * (sum(seat_diff)) / regions[0][0].n_seats)

        # Pie charts
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
            title="Final results",
            uniformtext_minsize=12,
            uniformtext_mode='hide',
            # Add annotations in the center of the donut pies.
            annotations=[dict(text='Sys. 1', x=0.18, y=0.5, font_size=20, showarrow=False),
                         dict(text='Sys. 2', x=0.82, y=0.5, font_size=20, showarrow=False)],
        )
        pie.update_layout(margin=dict(t=40, b=10, l=0, r=0))

    else:
        disable = True
        dropdown_style={'font-size': '20px', 'margin-top': '5px', 'backgroundColor': system_unselected_color}

        metrics = election.get_single_metrics(s1)

        lost_votes_percentage = list(metrics['lost_votes_percentage'].values())
        total_votes = sum(regions[0][0].votes.values())
        map_fig = go.Figure(go.Choroplethmapbox(
            geojson=election.country.regions()[level]['geojson'],
            locations=locations,
            z=lost_votes_percentage,
            colorscale="Reds",
            zmin=0, zmax=1,
            marker_line_width=1
        ))
        map_fig.update_layout(title='Percentage of Lost Votes per Region')

        party_lost_votes = metrics['party_lost_votes']
        total_lost_votes = sum(party_lost_votes.values())
        party_lost_votes = party_lost_votes.most_common(10)
        bar_colors = [election.colors[x[0]] if x[0] in election.colors else '#7D7D7D' for x in party_lost_votes]
        bar_fig = go.Figure(data=[go.Bar(
            x = [x[0] for x in party_lost_votes],
            y = [x[1] for x in party_lost_votes],
            marker_color = bar_colors,
        )])
        bar_title = 'Lost Votes per Party\t (Total Lost Votes: {:,} -- {:.2f}%)'.format(total_lost_votes, 100 * total_lost_votes / total_votes)
        bar_fig.update_layout(
            title_text=bar_title,
            yaxis=dict(
                title='Lost Votes',
                titlefont_size=16,
                tickfont_size=14,
            ),
        )
        bar_fig.update_layout(margin=dict(t=40, b=20, l=0, r=0))

        card_1_header = 'Total Lost Votes'
        card_1_title = '{:,}'.format(total_lost_votes)
        card_2_header = 'Total % of Lost Votes'
        card_2_title = "{:.2f}%".format(100 * total_lost_votes / total_votes)

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
        )
        pie.update_layout(margin=dict(t=40, b=10, l=0, r=0))
        #pie_fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))


    map_fig.update_layout(mapbox_style="light",
                          mapbox_accesstoken=MAPBOX_ACCESS_TOKEN,
                          mapbox_zoom=election.country.zoom(),
                          mapbox_center = election.country.center(),
                          margin={"r":0,"t":40,"l":0,"b":0},
                          height=900,
                          font={'size': 16})

    bar_fig.update_layout(font={'size': 16})

    pie.update_layout(font={'size': 16})

    return map_fig, bar_fig, pie, disable, disable, disable, dropdown_style, dropdown_style, dropdown_style


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True, port=800)
