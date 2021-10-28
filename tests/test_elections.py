import os
import pytest
import sys

from app import elections

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../app')

election_names = [
    'Spain_2019_11',
    'Spain_2019_04',
    'Spain_2016_06',
    'Spain_2015_12',
    'Spain_2011_11',
    'Spain_2008_03',
    'Spain_2004_03',
    'Spain_2000_03',
]


@pytest.mark.parametrize("election_name", election_names)
def test_instantiate_all_elections(election_name):
    election_class = getattr(elections, election_name)
    election_object = election_class()
    assert len(election_object.parties) > 0  # Just checking that the initialization is OK


@pytest.mark.parametrize("election_name", election_names)
def test_country_level_threshold(election_name):
    election_class = getattr(elections, election_name)
    election_object = election_class()

    max_n_parties = len(election_object.parties)
    for threshold in range(15):
        parties = election_object.get_valid_parties(threshold)
        assert 0 <= len(parties) <= max_n_parties
        max_n_parties = len(parties)
