from dash import Dash, html, dcc, no_update, Input, Output, State
import dash_bootstrap_components as dbc
from dash_daq import BooleanSwitch

# Custom modules
import countries
import elections
import electoral_systems

# Read the markdown files
with open('texts/about.md', 'r') as file:
    about_md = file.read()
with open('texts/country_election_metric.md', 'r') as file:
    country_md = file.read()
with open('texts/electoral_systems.md', 'r') as file:
    systems_md = file.read()

# initialize all the elections so that all the data loading is done when starting the app
ELECTIONS = {
    'Costa Rica': {
        '2018': elections.Costa_Rica_2018(),
    },
    'Spain': {
        '2019-11-10': elections.Spain_2019_11(),
        '2019-04-28': elections.Spain_2019_04(),
        '2016-06-26': elections.Spain_2016_06(),
        '2015-12-20': elections.Spain_2015_12(),
        '2011-11-20': elections.Spain_2011_11(),
        '2008-03-09': elections.Spain_2008_03(),
        '2004-03-14': elections.Spain_2004_03(),
        '2000-03-12': elections.Spain_2000_03(),
    },
    'USA': {
        '2020': elections.USA_2020()
    }
}

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.LUMEN])
server = app.server  # Necessary for deployment on DigitalOcean

##############
#   LAYOUT   #
##############

# STUFF THAT GOES IN THE SIDEBAR

dropdown_countries = dcc.Dropdown(
    id="dropdown-countries",
    options=[{'label': country, 'value': country} for country in countries.COUNTRY_LIST],
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
        {'label': 'Lost Votes', 'value': 'Lost Votes'},
    ],
    value='Seat Difference',
    placeholder='Metric',
    style={'font-size': '20px', 'margin-top': '5px'},
    clearable=False,
)

# BUTTONS
about_button = html.Div(
    [
        dbc.Button("About", id="about-button", n_clicks=0, size='lg', color='primary'),
        dbc.Modal(
            [dbc.ModalBody(dcc.Markdown(about_md))],
            id="about-modal",
            is_open=False,
            size='xl',
            scrollable=True,
            style={'font-size': '1.8em'}
        ),
    ],
    style={'justify-content': 'flex-end', 'display': 'flex'}
)

countries_button = html.Div(
    [
        dbc.Button("?", id="countries-button", n_clicks=0, color='primary'),
        dbc.Modal(
            [dbc.ModalBody(dcc.Markdown(country_md))],
            id="countries-modal",
            is_open=False,
            size='xl',
            scrollable=True,
            style={'font-size': '1.8em'}
        ),
    ],
    style={'justify-content': 'flex-end', 'display': 'flex'}
)

systems_button = html.Div(
    [
        dbc.Button("?", id="systems-button", n_clicks=0, color='primary'),
        dbc.Modal(
            [dbc.ModalBody(dcc.Markdown(systems_md))],
            id="systems-modal",
            is_open=False,
            size='xl',
            scrollable=True,
            style={'font-size': '1.8em'}
        ),
    ],
    style={'justify-content': 'flex-end', 'display': 'flex'}
)

system_1_dropdown = dcc.Dropdown(
    id="dropdown-system-name-1",
    options=[
        {'label': "d'Hondt", 'value': 'dHondt'},
        {'label': "Sainte-Laguë", 'value': 'SL'},  # https://en.wikipedia.org/wiki/Webster/Sainte-Lagu%C3%AB_method
        {'label': "Winner Takes All", 'value': "Winner Takes All"},
        {'label': "LRM (Hare Quota)", 'value': 'LRM-Hare'},  # https://en.wikipedia.org/wiki/Largest_remainder_method
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
            options=[{'label': str(x)+'%', 'value': str(x)} for x in range(16)] + [{'label': 'n/2s', 'value': 'n/2s'}],
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
        dbc.Col(systems_button, width=2),
    ]),
    system_1_dropdown,
    system_1_levels,
    system_1_threshold,
])

system_2_dropdown = dcc.Dropdown(
    id="dropdown-system-name-2",
    options=[
        {'label': "d'Hondt", 'value': 'dHondt'},
        {'label': "Sainte-Laguë", 'value': 'SL'},  # https://en.wikipedia.org/wiki/Webster/Sainte-Lagu%C3%AB_method
        {'label': "Winner Takes All", 'value': "Winner Takes All"},
        {'label': "LRM (Hare Quota)", 'value': 'LRM-Hare'},  # https://en.wikipedia.org/wiki/Largest_remainder_method
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
            options=[{'label': str(x)+'%', 'value': str(x)} for x in range(16)] + [{'label': 'n/2s', 'value': 'n/2s'}],
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

system_unselected_color = '#F4CCCC'

# GRAPHS

graphs = dbc.Row([
    dbc.Col(html.Div([
            dcc.Graph(id='chart'),
            dcc.Graph(id='pie-1')]
        ),
        xl=7, lg=7, md=12, sm=12, xs=12,
    ),
    dbc.Col(html.Div([
            dcc.Graph(id='map', clear_on_unhover=True),
            dcc.Tooltip(id="graph-tooltip", direction="bottom")]
        ),
        xl=5, lg=5, md=12, sm=12, xs=12,
    ),
])

# STYLES AND FINAL LAYOUT

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "22rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H3("Comparing Electoral Systems", id='dashboard-title'),
        about_button,
        html.Hr(),
        dbc.Row([
            dbc.Col(html.P("Select country, election date and metric to be displayed", className="lead"), width=10),
            dbc.Col(countries_button, width=2)]
        ),
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
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(graphs, style=CONTENT_STYLE)

app.layout = html.Div([
        sidebar,
        content,
    ],
)

print("Everything is loaded!")

#############
# CALLBACKS #
#############


# Make this callback on the client side?
@app.callback(
    Output('dropdown-elections', 'options'),
    Output('dropdown-elections', 'value'),
    Output('dropdown-region-level-1', 'options'),
    Output('dropdown-region-level-1', 'value'),
    Output('dropdown-region-level-2', 'options'),
    Output('dropdown-region-level-2', 'value'),
    Input('dropdown-countries', 'value'),
)
def switch_country(country):
    """
    Update the election options whenever the selected country changes.
    """
    if country == 'Costa Rica':
        election_options = [
            {'label': '2018', 'value': '2018'},
        ]
        election_value = '2018'

        level_options = [
            {'label': '0: Country', 'value': 0},
            {'label': '1: Province', 'value': 1},
        ]
        level_value = 1
    elif country == 'Spain':
        election_options = [
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

        level_options = [
            {'label': '0: Country', 'value': 0},
            {'label': '1: Aut. Community', 'value': 1},
            {'label': '2: Province', 'value': 2},
        ]
        level_value = 2
    elif country == 'USA':
        election_options = [
            {'label': '2020', 'value': '2020'},
        ]
        election_value = '2020'

        level_options = [
            {'label': '0: Country', 'value': 0},
            {'label': '1: State', 'value': 1},
            {'label': '2: District', 'value': 2},
        ]
        level_value = 2
    return election_options, election_value, level_options, level_value, level_options, max(0, level_value-1)


@app.callback(
    Output("about-modal", "is_open"),
    Input("about-button", "n_clicks"),
    State("about-modal", "is_open"),
)
def toggle_about_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open


@app.callback(
    Output("countries-modal", "is_open"),
    Input("countries-button", "n_clicks"),
    State("countries-modal", "is_open"),
)
def toggle_countries_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open


@app.callback(
    Output("systems-modal", "is_open"),
    Input("systems-button", "n_clicks"),
    State("systems-modal", "is_open"),
)
def toggle_systems_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open


@app.callback(
    Output('map', 'figure'),
    Output('chart', 'figure'),
    Output('pie-1', 'figure'),
    Output('dropdown-system-name-2', 'disabled'),
    Output('dropdown-region-level-2', 'disabled'),
    Output('threshold-2', 'disabled'),
    Output('dropdown-system-name-2', 'style'),
    Output('dropdown-region-level-2', 'style'),
    Output('threshold-2', 'style'),
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
    State('dropdown-countries', 'value'),
)
def update_figures(metric, system_name_1, level_1, threshold_1, threshold_1_country,
                   system_name_2, level_2, threshold_2, threshold_2_country, election_date,
                   country):
    """
    Dash callback to display the figures according to the parameters specified
    by the user.

    The callback is triggered whenever the metric to be displayed is modified,
    or whenever any parameter either in system 1 or system 2 changes.
    This callbacks modifies all three figures of the dashboard: The bar chart,
    the pie chart and the map.
    """
    election = ELECTIONS[country][election_date]
    regions = election.regions
    country_region = next(iter(regions[0].values()))

    system_1 = electoral_systems.System(system_name_1, level_1, threshold_1, threshold_1_country)
    result_1 = country_region.compute_result(system_1)

    if metric == 'Seat Difference':
        disable = False
        dropdown_style = {'font-size': '20px', 'margin-top': '5px'}

        system_2 = electoral_systems.System(system_name_2, level_2, threshold_2, threshold_2_country)
        result_2 = country_region.compute_result(system_2)

        map = result_1.get_map_plot(other=result_2)
        pie = result_1.get_piechart_plot(other=result_2)
        bar = result_1.get_bar_plot(metric, other=result_2)

    elif metric == 'Lost Votes':
        disable = True
        dropdown_style = {'font-size': '20px', 'margin-top': '5px', 'backgroundColor': system_unselected_color}

        map = result_1.get_map_plot()
        pie = result_1.get_piechart_plot()
        bar = result_1.get_bar_plot(metric)

    else:
        raise ValueError("You got the metric name wrong!")

    return map, bar, pie, disable, disable, disable, dropdown_style, dropdown_style, dropdown_style


@app.callback(
    Output("graph-tooltip", "show"),
    Output("graph-tooltip", "bbox"),
    Output("graph-tooltip", "children"),
    Input("map", "hoverData"),
    State("dropdown-countries", "value"),
    State("dropdown-elections", "value"),
    State("dropdown-metrics", "value"),
    State('dropdown-system-name-1', 'value'),
    State('dropdown-region-level-1', 'value'),
    State('threshold-1', 'value'),
    State('threshold-switch-1', 'on'),
    State('dropdown-system-name-2', 'value'),
    State('dropdown-region-level-2', 'value'),
    State('threshold-2', 'value'),
    State('threshold-switch-2', 'on'),
)
def display_tooltip(hoverData, country, election_date, metric, system_name_1, level_1,
                    threshold_1, threshold_country_1, system_name_2, level_2,
                    threshold_2, threshold_country_2):
    """
    Dash callback to display a tooltip when the user hovers on the map regions.

    The tooltip shows information that is relevant to the given region, given
    the parameters specified by the user on the sidebar.
    """
    if hoverData is None:
        return False, no_update, no_update

    bbox = hoverData["points"][0]["bbox"]
    region_name = hoverData["points"][0]["location"]

    election = ELECTIONS[country][election_date]

    if metric == 'Seat Difference':
        level = min(level_1, level_2)
    else:
        level = level_1
    region = election.get_region(level, region_name)

    system_1 = electoral_systems.System(system_name_1, level_1, threshold_1, threshold_country_1)
    result_1 = region.compute_result(system_1)

    if metric == 'Seat Difference':
        system_2 = electoral_systems.System(system_name_2, level_2, threshold_2, threshold_country_2)
        result_2 = region.compute_result(system_2)
        tooltip = result_1.plot_tooltip(other=result_2)
    elif metric == 'Lost Votes':
        tooltip = result_1.plot_tooltip()
    else:
        raise ValueError("You got the metric name wrong!")

    return True, bbox, dcc.Graph(figure=tooltip)


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=False, port=8080)
