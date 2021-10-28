import geojson
import os

COUNTRY_LIST = [
    'Spain',
    'USA',
]


class Country():
    """
    Class representing a country.

    ...
    Attributes
    ----------
    center: dict
        A dictionary {lat: x, lon: y} representing the coordinates where the
        country map should be centered at.
    zoom: int
        Represents the zoom used to plot the country map.
    regions: dict
        A dictionary with data about the regions of the country.
        Keys are the levels of the regions.
        Values are the geojsons containing the boundaries of the regions on that
        level; the id associated to a polygon needs to be the name of the
        region.
        Only level 0 is mandatory.

    Methods
    -------
    get_regions(level): List
        Return the geojson string containing all the region boundaries at a
        given level.
    """
    def __init__(self, name: str):
        self.name = name
        return

    @property
    def center(self):
        """
        The center of the map to be plotted. It needs to be a dictionary with
        the keys 'lat' and 'lon'.
        """
        return {'lat': self._center[0], 'lon': self._center[1]}

    @center.setter
    def center(self, latlon):
        try:
            lat, lon = latlon
        except ValueError:
            raise ValueError("Pass an iterable with two items (lat, lon)")
        if not -90 <= lat <= 90:
            raise ValueError("Latitude must be a value between -90 and 90.")
        if not -180 <= lon <= 180:
            raise ValueError("Longitude must be a value between -180 and 180.")
        self._center = (lat, lon)

    @property
    def zoom(self):
        """
        An integer representing the zoom used to plot the map.
        See https://docs.mapbox.com/help/glossary/zoom-level/ for reference.
        """
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        if value not in [x for x in range(23)]:
            raise ValueError("Map zoom must be an integer between 0 and 22.")
        self._zoom = value

    @property
    def regions(self):
        """
        A dictionary with data about the regions of the country.
        Keys are the levels of the regions.
        Values are the geojsons containing the boundaries of the regions on that
        level; the id associated to a polygon needs to be the name of the
        region.
        Only level 0 is mandatory.
        """
        return self._regions

    @regions.setter
    def regions(self, value):
        if 0 not in value:
            raise ValueError("A country-level region (0) must be specified")
        if len(value) != len(set(value)):
            raise ValueError("Region levels must be unique.")
        self._regions = value

    def get_geojson(self, level):
        """
        Return the geojson string containing all the region boundaries at a
        given level.
        """
        return self._regions[level]


class Spain(Country):
    """
    Class representing Spain.
    """
    def __init__(self):
        super(Spain, self).__init__('Spain')
        self.center = (40.3152161, -3.8320321)  # lat, lon
        self.zoom = 4

        with open(os.path.join(os.path.dirname(__file__), 'data/Spain/level_0.geojson')) as f:
            level_0 = geojson.load(f)
        with open(os.path.join(os.path.dirname(__file__), 'data/Spain/level_1.geojson')) as f:
            level_1 = geojson.load(f)
        with open(os.path.join(os.path.dirname(__file__), 'data/Spain/level_2.geojson')) as f:
            level_2 = geojson.load(f)
        self.regions = {
            0: level_0,
            1: level_1,
            2: level_2,
        }

class USA(Country):
    """
    Class representing the United States of America.
    """
    def __init__(self):
        super(USA, self).__init__('USA')
        self.center = (41.2, -97.5)
        self.zoom = 2

        with open(os.path.join(os.path.dirname(__file__), 'data/USA/level_0.geojson')) as f:
            level_0 = geojson.load(f)
        with open(os.path.join(os.path.dirname(__file__), 'data/USA/level_1.geojson')) as f:
            level_1 = geojson.load(f)
        with open(os.path.join(os.path.dirname(__file__), 'data/USA/level_2.geojson')) as f:
            level_2 = geojson.load(f)
        self.regions = {
            0: level_0,
            1: level_1,
            2: level_2,
        }
