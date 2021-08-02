from abc import ABC, abstractmethod
from bidict import bidict
import geopandas
import json
import pickle

COUNTRY_LIST = [
    'Spain'
]

countries_gdf = geopandas.read_file('data/countries.geojson')

class Country(ABC):
    def __init__(self, name: str):
        self.name = name
        return

    @property
    @abstractmethod
    def center(self):
        """
        The center of the map to be plotted. It needs to be a dictionary with
        the keys 'lat' and 'lon'.
        """
        pass

    @property
    @abstractmethod
    def zoom(self):
        """
        An integer representing the zoom used to plot the map.
        """
        pass

    @property
    @abstractmethod
    def regions(self):
        """
        A dictionary with data about the regions of the country.
        Keys are the levels of the regions (0,1,2,3).
        Values are dictionaries themselves, with 2 key-value pairs:
            'geojson': the geojson with all the region boundaries with ids
            'regions': Values are dict with the region codes and names as kvps.
        Only level 0 is mandatory.
        """
        pass


class Spain(Country):
    def __init__(self):
        super(Spain, self).__init__('Spain')
        self._regions = self.parse_regions()

    def center(self):
        return {'lat': 40.3152161, 'lon': -3.8320321}

    def zoom(self):
        return 4

    def regions(self):
        return self._regions

    def parse_regions(self):
        with open('data/Spain/regions_level_1.pkl', 'rb') as f:
            level_1_data = pickle.load(f)

        with open('data/Spain/regions_level_2.pkl', 'rb') as f:
            level_2_data = pickle.load(f)

        spain_geojson = countries_gdf.loc[countries_gdf['ADMIN'] == 'Spain']['geometry'].to_json()
        spain_geojson = json.loads(spain_geojson)
        spain_geojson['features'][0]['id'] = 'Spain'
        result = {0: {
                'geojson': spain_geojson,
                'regions': 'Spain',
            },
            1: level_1_data,
            2: level_2_data,
        }
        return result
