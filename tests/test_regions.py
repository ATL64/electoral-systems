from itertools import product
import os
import pytest
import sys

from app import elections, electoral_systems

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../app')

system_names = electoral_systems.SYSTEM_NAMES
dummy_threshold = 3
dummy_level = 1
t_systems = dict()
for s in system_names:
    t_systems[s] = electoral_systems.System(s, dummy_level, dummy_threshold)

t_elections = [
    elections.Spain_2019_11(),
    elections.Spain_2019_04(),
    elections.Spain_2016_06(),
    elections.Spain_2015_12(),
    elections.Spain_2011_11(),
    elections.Spain_2008_03(),
    elections.Spain_2004_03(),
    elections.Spain_2000_03(),
]

t_levels = [0, 1, 2]
country_level_trheshold = [True, False]

input_combinations = list(product(t_elections, list(t_systems), t_levels, country_level_trheshold))


# For every country, for every election, for every level, pick randomly 3 regions and test election result with every method
@pytest.mark.parametrize("input", input_combinations)
def test_election_result(input):
    election, system_name, level, clt = input
    system = t_systems[system_name]
    system.threshold_country = clt
    for region in election.get_regions(level).values():
        result = region.compute_election_result(system)
        assert sum(result.values()) == region.n_seats


# TODO Given two different systems, check that the +- in seat difference equals to 0.
