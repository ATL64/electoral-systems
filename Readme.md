# Comparing Electoral Systems

![Tests](https://github.com/alejandrodemiquel/electoral-systems/actions/workflows/tests.yml/badge.svg)

This repository contains a [dash](https://plotly.com/dash/) app aimed at
visualising and analysing the effects that using different electoral systems
would have had in past parliamentary elections.
The app is currently hosted at
[https://electoral-systems-qvlqe.ondigitalocean.app/](https://electoral-systems-qvlqe.ondigitalocean.app/).

The app itself is contained in the folder `app`.
The folder `data` contains information about the data sources that were used
to build the app, as well as the preprocessing scripts that were used to
generate all the files present in the folder `app/data`.
Therefore, all the workflows are completely reproducible.

## Contributing

Anyone can contribute by making suggestions and reporting bugs.
Feel free to open an issue or send us an email to alejandrodemiquel@gmail.com.

## Development Guide

Everyone who wants is welcome to make pull requests with improvements;
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
Once an `Electoral_Region` is defined, given a `System`, one can use its method
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

Code-wise, you just need to add a class in the file `countries.py` that inherits
from `Country` and add the map center, the map zoom and the geojson strings
containing the borders of every region at every level.
You can follow the class `Spain` as an example.
You also need to add the name of your country to the `COUNTRY_LIST` defined in
`countries.py`.

You will probably read the geojsons from some files. These files need to be
stored in the folder `app/data/YOUR_COUNTRY_NAME`.
You might find the boundary of your country (level 0) in the file
`app/data/countries.geojson`.

You will also need to add the source of your data in the file
`data/Data_Sources.txt`, as well as the raw data from that source in the folder
`data/YOUR_COUNTRY_NAME`, together with any code that you have used to
preprocess it.
Again, you can follow `Spain` as an example.

Finally, you will need to specify what happens when your country is selected in
the dropdown menu: you will need to modify the callback `switch_country`.

### Adding a new election

In order to add a new election of an already supported country, you will need
to add a class in the file `elections.py` that inherits from `Election`.

This class will need to define the attributes `country`, `regions`, `parties`,
`colors`, and `electoral_system`. They are all defined in `Election`'s
docstring.
All of them should be straightforward to implement except for `regions`.

`regions` is the object that contains the actual information about the results
of the election.
It is a collection of objects of the class `Electoral_Region`, defined in the
file `regions.py`.
For each `Electoral_Region` that you define, you will need to specify the
following information about the real electoral results:

- `name`: The name of the region.
- `level`: The level of the region.
- `census`: The total number of votes registered in the region.
- `n_seats`: The total number of parliament seats elected in the region.
- `votes`: Keys are party names, values are the number of votes that they
  obtained in the region.
- `nota`: Number of 'None of the Above' votes.
- `spoilt_votes`: Number of spoilt votes

Moreover, each `Electoral_Region` object also needs to have an attribute called
`subregions`, which is a list of `Electoral_Regions` that is exactly one lever
lower and that are actually subregions of the given region.
In the case of Spain, this is done in the `Spain_Election` method
`_build_region_tree`.
However, this approach might not be the optimal one; feel free to build your
`Election` object the way you find best.

Once you have defined your election, you will need to add it in the `ELECTIONS`
dictionary of `main.py` in order for it to be displayed as an option in the
dashboard.

With this you should be all set, but we also ask you to upload your data sources
and any preprocessing scripts that you may have used.
Similarly to the case of the `Country` classes, we ask you to add the files that
you use in the folder `app/data/YOUR_COUNTRY_NAME`.
We also ask you to add the source of your election data in the file
`data/Data_Sources.txt`, as well as the raw data from that source in the folder
`data/YOUR_COUNTRY_NAME`, together with any code that you have used to
preprocess it.
Again, you can follow `Spain` as an example.

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
