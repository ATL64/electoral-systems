# Comparing Electoral Systems

![Tests](https://github.com/Valiant-Data/electoral-systems/actions/workflows/tests.yml/badge.svg)

Main contributor for this project is Alejandro de Miquel who is a fantastic coder and scientist with great expertise in everything data related. You can see some of his awesome work here: https://github.com/alejandrodemiquel 


This repository contains a [Dash](https://plotly.com/dash/) app aimed at
visualising and analysing the effects that using different electoral systems
would have had in past parliamentary elections (house of representatives).
The app is currently offline.  But here is a screenshot of how it looks like:


The app itself is contained in the folder `app`.
The folder `data` contains information about the data sources that were used
to build the app, as well as the preprocessing scripts that were used to
generate all the files present in the folder `app/data`.
Therefore, all the workflows are completely reproducible.

## Contributing

Anyone can contribute by making suggestions and reporting bugs.
Feel free to open an issue or send us an email to alejandrodemiquel@gmail.com or atl64x@gmail.com

## Development Guide

Everyone is welcome to make pull requests with improvements,
be it bug fixes, performance improvements, adding analysis metrics, adding
countries or modifying the layout/appearance of the app.

If you decide to contribute, please publish a pull request and we will review it
as soon as we can.

### Understanding the app

All the relevant files that you need to understand are under the folder `app`.
In particular,

- `main.py` is where the Dash app, the layout and the callbacks are defined.

- `countries.py` defines the class `Country`, which serves as a parent class to
classes that contain information about particular countries, such as the
geojson with the region boundaries or the zoom to be used in the map.

- `elections.py` defines the class `Election`, which serves as a parent class to
classes that contain information about elections that were held in the past.

- `electoral_systems.py` defines the class `System`, containing information
about particular electoral systems.

- `regions.py` defines the classes `Electoral_Region` and `Electoral_Result`.
An `Electoral_Region` contains information about how many votes each party got
in a particular region at a given election.
Once an `Electoral_Region` is defined, one can use its method
`compute_election_result` to obtain the result on that region given a particular
electoral system.
The result is returned as an object of the class `Electoral_Result`.
This object contains all sorts of methods to compute the metrics derived from
that result, as well as to build the choropleth maps, the pie charts and the
bar charts.

### Adding a new metric

Currently we are supporting the metrics:

- Seat Difference
- Lost Votes

However, we are open to add more insightful metrics.
If you want to add one yourself, all you need to do is:

1. Add your option in `main.py`'s `dropdown_metrics`.

2. Define what to do when your metric is selected in `main.py`'s callbacks
`update_figures` and `display_tooltip`. You will need to think of what you plot
in the upper figure, in the lower figure, in the choropleth maps and in the
map tooltips.

3. Add the relevant method in `regions.Election_Result`. You can use the
methods `get_seat_diff` and `get_lost_votes` to have an idea on how to implement
your own method.

4. Modify the `regions.Election_Result` methods `plot_tooltip`, `get_map_plot`,
`get_piechart_plot` and `get_bar_plot` if necessary, so that the figures show
what you want them to show whenever your option is selected.

### Adding a new country

Adding a new country without any elections associated is easy to do and is the
first step that needs to be done if you want to add an election of a country
that is not supported yet.
In order to do so, you need to follow these steps:

1. Download the borders of all the regions that you want to consider for this
country, at every level (electoral district, province, state...) and store them
under `data/YOUR_COUNTRY_NAME`.
Also, add the data sources in `data/Data_Sources.txt`.
You might find the boundary of your country (level 0) in the file
`app/data/countries.geojson`.

2. Preprocess them in order to have them in the correct format for the app:
For every region level, build a geojson file making sure that the id of every
region's polygon corresponds to the region name. Save these files under
`app/data/YOUR_COUNTRY_NAME/level_x.geojson`, where `x` refers to the level of
the regions contained in that file.
If you use any python file to preprocess your data, store it under
`data/YOUR_COUNTRY_NAME/preprocess_data.py`

3. Add a class in the file `countries.py` that inherits from `Country` and add
the map center, the map zoom and the geojson strings containing the borders of
every region at every level. You can follow the class `Spain` as an example.

4. Add the name of your country to the `COUNTRY_LIST` defined in `countries.py`.

5. Specify what happens when your country is selected in the dropdown menu:
you will need to modify the callback `switch_country`.

### Adding a new election

In order to add a new election of an already supported country, follow these
steps:

1. Download the election data from a reliable source. Store the data under
`data/YOUR_COUNTRY_NAME` with a name that relates to the particular election.
Specify the data source in `data/Data_Sources.txt`.

2. Preprocess the data in order to have it in the right format, and store the
python file used for preprocessing the data under `data/YOUR_COUNTRY_NAME`.
The current format is a pickle file whose object is a dictionary containing
a list with the parties participating in the election and a dictionary of
regions, divided by levels, and with each region having the following
information:
    - `name`: The name of the region.
    - `level`: The level of the region.
    - `census`: The total number of votes registered in the region.
    - `n_seats`: The total number of parliament seats elected in the region.
    - `votes`: Keys are party names, values are the number of votes that they
obtained in the region.
    - `nota`: Number of 'None of the Above' votes.
    - `spoilt_votes`: Number of spoilt votes
You can use Spain as an example.
The file with the preprocessed data will be read by the `Election` internal
method `_parse_data`.
If you want to use a different format, feel free to modify the `_parse_data`
method or add an alternative one.

3. Define a class in the file `elections.py` that inherits from `Election`.
This class will need to define the attributes `country`, `regions`, `parties`,
`colors`, and `electoral_system`. They are all defined in `Election`'s
docstring.

4. Each `Electoral_Region` object also needs to have an attribute called
`subregions`, which is a list of `Electoral_Regions` that is exactly one lever
lower and that are actually subregions of the given region.
In the case of Spain and the USA, this is done in the method
`_build_region_tree`.

5. Add the election object in the `ELECTIONS` dictionary of `main.py` in order
for it to be displayed as an option in the dashboard.

### Testing

If you modify any of the source code, make sure you run the tests locally before
submitting a pull request.
In order to execute them, you need to run these two commands from the root
directory:

```
flake8
pytest tests
```

`pytest` is the framework that we are using for running our functional tests.
`Flake8` checks that the python code follows all the python standards.
You will need to have both of them installed.

Just adding tests, without making any source code contribution, is another good
way to contribute to this project.
Currently, our tests are quite basic. They make sure that things are initialized
correctly and do some other simple checks.
We could make use of some contributions to test that each method gives expected
results.


