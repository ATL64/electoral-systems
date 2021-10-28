import pytest

from app import countries


@pytest.mark.parametrize("country_name", countries.COUNTRY_LIST)
def test_instantiate_all_countries(country_name):
    country_class = getattr(countries, country_name)
    country_object = country_class()
    assert 0 < country_object.zoom < 25  # Just checking that the object is porperly initialised
