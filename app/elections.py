import os
import pickle
import plotly.graph_objects as go
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath)

import countries  # noqa: E402
from regions import Electoral_Region  # noqa: E402
import electoral_systems  # noqa: E402


class Election():
    """
    Class representing an parliamentary election that was held in the past.

    ...
    Attributes
    ----------
    date: str
        The date on which the election was held, in the format 'YYYY-MM-DD'.
    country: countries.Country
        The country where the election was held.
    regions: dict
        A dictionary containing information about the election regions.
        Keys are region levels, values are dictionaries.
        The keys of these dictionaries are region names, and their values are
        the corresponding Electoral_Region.region objects.
    parties: list
        A list of the parties taking part in the election.
    colors: dict
        A dictionary whose keys are party names and values are the
        corresponding colors to be used on the plots (Hex color code).
    electoral_system: electoral_systems.System
        An object of the class electoral_systems.System containing the
        information about the system used on the election.

    Methods
    -------
    get_region(level, name): Electoral_Regions.region
        Given a regional level and a region name, return the Electoral_Regions.region
        object corresponding to that region.
    get_regions(level): dict
        Given a region level, return a dict containing all the Electoral_Regions.region
        objects corresponding to that level. Keys of the dictionary are region names.
    get_valid_parties(threshold): list
        For a particular election, given a national-level threshold, return
        a list of parties that have a number of votes above that threshold.
    """
    def __init__(self, country: countries.Country, date: str = None):
        self.date = date
        self.country = country
        self.maps = {
            0: go.Figure(go.Choroplethmapbox(
                geojson=self.country.get_geojson(0),
                locations=[x for x in self.regions[0]],
                z=[0] * len(self.regions[0]),
                colorscale="Reds",
                zmin=0, zmax=1,
                marker_line_width=1,
                hoverinfo='none',
            )),
            1: go.Figure(go.Choroplethmapbox(
                geojson=self.country.get_geojson(1),
                locations=[x for x in self.regions[1]],
                z=[0] * len(self.regions[1]),
                colorscale="Reds",
                zmin=0, zmax=1,
                marker_line_width=1,
                hoverinfo='none',
            )),
            2: go.Figure(go.Choroplethmapbox(
                geojson=self.country.get_geojson(2),
                locations=[x for x in self.regions[2]],
                z=[0] * len(self.regions[2]),
                colorscale="Reds",
                zmin=0, zmax=1,
                marker_line_width=1,
                hoverinfo='none',
            ))
        }

    @property
    def regions(self):
        """
        A dictionary. Keys are region levels, values are dictionaries.
        The keys of these dictionaries are region names, and their values are
        the corresponding Electoral_Region.region objects.
        """
        return self._regions

    @regions.setter
    def regions(self, value):
        if not type(value) == dict:
            raise TypeError("Election's 'region' attribute must be a dictionary.")
        for key in value:
            if not 0 <= key <= 5:
                raise ValueError("Keys representing levels must have values between 0 and 5.")
        self._regions = value

    @property
    def parties(self):
        """
        A list of the parties taking part in the election.
        """
        return self._parties

    @parties.setter
    def parties(self, value):
        if not type(value) == list:
            raise TypeError("Election's 'parties' attribute must be a list.")
        self._parties = value

    @property
    def colors(self):
        """
        A dictionary whose keys are party names and values are the
        corresponding colors to be used on the plots (Hex color code).
        """
        return self._colors

    @colors.setter
    def colors(self, value):
        if not type(value) == dict:
            raise TypeError("Election's 'colors' attribute must be a dictionary.")
        self._colors = value

    @property
    def electoral_system(self):
        """
        An object of the class electoral_systems.System containing the
        information about the system used on the election.
        """
        return self._electoral_system

    @electoral_system.setter
    def electoral_system(self, value):
        if not type(value) == electoral_systems.System:
            raise TypeError("The Election's electoral_system must be an object of electoral_systems.System.")
        self._electoral_system = value

    def get_region(self, level, name):
        """
        Given a regional level and a region name, return the Electoral_Regions.region
        object corresponding to that region.
        """
        return self.regions[level][name]

    def get_regions(self, level):
        """
        Given a region level, return a dict containing all the Electoral_Regions.region
        objects corresponding to that level. Keys of the dictionary are region names.
        """
        return self.regions[level]

    def get_valid_parties(self, threshold):
        """
        For a particular election, given a national-level threshold, return
        a list of parties that have a number of votes above that threshold.
        """
        total_votes = sum(self._regions[0][self.country.name].votes.values())
        vote_threshold = total_votes * threshold / 100

        parties = [p for p, v in self._regions[0][self.country.name].votes.items() if v >= vote_threshold]

        return parties

    def _parse_data(self, filename):
        """
        Extract the data from the pickle file, initialize the Electoral_Regions.region
        objects and format the data for it to be used as attributes of an object of
        the class Election.
        """
        with open(filename, 'rb') as f:
            data = pickle.load(f)

        level_0_electoral_region = dict()
        level_0_electoral_region[data['data'][0]['region_name']] = Electoral_Region(
            self,
            data['data'][0]['region_name'],
            data['data'][0]['level'],
            data['data'][0]['census'],
            data['data'][0]['n_seats'],
            data['data'][0]['votes'],
            data['data'][0]['nota'],
            data['data'][0]['split_votes'],
        )

        level_1_electoral_regions = dict()
        for region, results in data['data'][1].items():
            level_1_electoral_regions[results['region_name']] = Electoral_Region(
                self,
                results['region_name'],
                results['level'],
                results['census'],
                results['n_seats'],
                results['votes'],
                results['nota'],
                results['split_votes'],
            )

        level_2_electoral_regions = dict()
        for region, results in data['data'][2].items():
            level_2_electoral_regions[results['region_name']] = Electoral_Region(
                self,
                results['region_name'],
                results['level'],
                results['census'],
                results['n_seats'],
                results['votes'],
                results['nota'],
                results['split_votes'],
            )

        electoral_regions = {
            0: level_0_electoral_region,
            1: level_1_electoral_regions,
            2: level_2_electoral_regions,
        }
        return {'parties': data['parties'], 'regions': electoral_regions}


#########
# SPAIN #
#########

# Define some variables that are common to every Spain_Election
spain_country = countries.Spain()
spain_colors = {  # See https://en.wikipedia.org/wiki/Category:Spain_political_party_colour_templates
    'AMAIUR': '#087178',
    'ARALAR-ZUTIK': '#BD0000',  # 2004
    'BLOC-EV': '#4E9E41',  # 2004
    'BLOC-VERDS': '#4E9E41',
    'BNG': '#ADCFEF',
    'B.N.G.': '#ADCFEF',
    'BNG-NÓS': '#ADCFEF',
    'NÓS': '#ADCFEF',
    'CA': '#006633',  # Coalición Andalucista, 2008
    'CC': '#FFD700',
    'CC-PNC': '#FFD700',
    'CCa-PNC-NC': '#FFD700',
    'CCa-PNC': '#FFD700',
    'CC-NC-PNC': '#FFD700',
    'CDC': '#18307B',
    'CHA': '#008A21',  # Chunta Aragonesista, 2004
    'CIU': '#18307B',
    'CiU': '#18307B',
    'DL': '#18307B',
    'Cs': '#EB6109',
    "C's": '#EB6109',
    'COMPROMÍS 2019': '#DA5C31',
    'COMPROMÍS-Q': '#DA5C31',
    'CUP-PR': '#FFED00',
    'EA': '#77AC1C',  # Eusko-Alkartasuna, 2004
    'EAJ-PNV': '#4AAE4A',
    'Eb': '#DDDDDD',  # Escaños en blanco, 2011
    'CENB': '#DDDDDD',  # 2004
    'ECP-GUANYEM EL CANVI': '#5A205A',
    'ECP': '#5A205A',
    'EH Bildu': '#B5CF18',
    'EN COMÚ': '#5A205A',
    'EQUO': '#8ABA18',
    'ERC': '#8ABA18',
    'ERC-CATSÍ': '#FFB232',
    'ERC-CATSI': '#FFB232',
    'ERC-SOBIRANISTES': '#FFB232',
    'ESQUERRA': '#FFB232',
    'FAC': '#10286B',
    'FRONT REPUBLICÀ': '#EB2071',  # 2019
    'GIL': '#029138',  # 2000
    'IC-V': '#4E9E41',  # Iniciativa per Catalunya, 2000
    'IU': '#D56545',
    'I.U.': '#D56545',
    'IU-LV': '#D56545',
    'IU-UPeC': '#D56545',
    'JxCAT-JUNTS': '#5AB6A1',
    'MÁS PAÍS-EQUO': '#0FDEC4',
    'MÉS': '#D8DE40',
    'MÉS COMPROMÍS': '#DA5C31',
    'Na-Bai': '#F75E42',
    'NA-BAI': '#F75E42',
    'GBAI': '#F75E42',
    'MÁS PAÍS': '#0FDEC4',  # 2019
    'NA+': '#819DA3',
    'NC-CCN': '#BAF73E',
    'Nca': '#639E42',
    'PA': '#005931',  # Partido Andalucista, 2004
    'PAR': '#FFCC66',  # Partido Aragonés, 2008
    'PACMA': '#ADBE18',
    'PP': '#007FFF',
    'P.P.': '#007FFF',
    'PRC': '#C2CE0C',
    'P.R.C.': '#C2CE0C',
    'PSM-EN,EU,EV,ER': '#FF9933',  # Progressistes per les Illes Balears, 2004
    'PSOE': '#FF0000',
    'P.S.O.E.': '#FF0000',
    'PSOE-PROGR.': '#FF0000',
    'PODEMOS': '#5A205A',
    'PODEMOS-En': '#5A205A',
    'PODEMOS-EN MAREA-ANOVA-EU': '#5A205A',
    'PODEMOS-EU-MAREAS EN COMÚN-EQUO': '#5A205A',
    'PODEMOS-COM': '#5A205A',
    'PODEMOS-COMPROMÍS-EUPV': '#5A205A',
    'PODEMOS-EU': '#5A205A',
    'PODEMOS-IU': '#5A205A',
    'PODEMOS-IU-EQUO': '#5A205A',
    'PxC': '#444042',  # 2011
    'RECORTES CERO-GV': '#00862A',  # 2019
    'RECORTES CERO-GRUPO VERDE': '#00862A',
    'RECORTES CE': '#00862A',
    'unio.cat': '#18307B',
    'UPL': '#B41062',  # Unión del Pueblo Leonés, 2000
    'UPYD': '#E9008C',
    'UPyD': '#E9008C',
    'UV': '#1F4473',  # Unió Valenciana, 2000
    'VERDES': '#099E40',  # 2008
    'LV-E': '#099E40',  # 2004
    'VOX': '#63BE21',
    '¡TERUEL EXISTE!': '#037252',
}

spain_ccaa_and_provinces = {}
for x in ['Almería', 'Cádiz', 'Córdoba', 'Granada', 'Huelva', 'Jaén', 'Málaga', 'Sevilla']:
    spain_ccaa_and_provinces[x] = 'Andalucía'
for x in ['Huesca', 'Teruel', 'Zaragoza']:
    spain_ccaa_and_provinces[x] = 'Aragón'
spain_ccaa_and_provinces['Cantabria'] = 'Cantabria'
for x in ['Ávila', 'Burgos', 'León', 'Palencia', 'Salamanca', 'Segovia', 'Soria', 'Valladolid', 'Zamora']:
    spain_ccaa_and_provinces[x] = 'Castilla y León'
for x in ['Albacete', 'Ciudad Real', 'Cuenca', 'Guadalajara', 'Toledo']:
    spain_ccaa_and_provinces[x] = 'Castilla-La Mancha'
for x in ['Barcelona', 'Girona', 'Lleida', 'Tarragona']:
    spain_ccaa_and_provinces[x] = 'Cataluña'
spain_ccaa_and_provinces['Ceuta'] = 'Ceuta y Melilla'
spain_ccaa_and_provinces['Melilla'] = 'Ceuta y Melilla'
spain_ccaa_and_provinces['Madrid'] = 'Comunidad de Madrid'
spain_ccaa_and_provinces['Navarra'] = 'Comunidad Foral de Navarra'
for x in ['Alacant', 'Castelló', 'València']:
    spain_ccaa_and_provinces[x] = 'Comunidad Valenciana'
spain_ccaa_and_provinces['Badajoz'] = 'Extremadura'
spain_ccaa_and_provinces['Cáceres'] = 'Extremadura'
for x in ['A Coruña', 'Lugo', 'Ourense', 'Pontevedra']:
    spain_ccaa_and_provinces[x] = 'Galicia'
spain_ccaa_and_provinces['Illes Balears'] = 'Islas Baleares'
spain_ccaa_and_provinces['Las Palmas'] = 'Islas Canarias'
spain_ccaa_and_provinces['Santa Cruz de Tenerife'] = 'Islas Canarias'
spain_ccaa_and_provinces['La Rioja'] = 'La Rioja'
for x in ['Araba', 'Bizkaia', 'Gipuzcoa']:
    spain_ccaa_and_provinces[x] = 'País Vasco'
spain_ccaa_and_provinces['Asturias'] = 'Principado de Asturias'
spain_ccaa_and_provinces['Murcia'] = 'Región de Murcia'


class Spain_Election(Election):
    """
    Parent class to all the classes that represent elections that were held
    in Spain.
    """
    def __init__(self, data_file: str):
        """
        Parameters
        ----------
        data_file: str
            The path of the pickle file containing the electoral results.
        """
        date = data_file.split('_')[-1].split('.')[0]  # The date of the election is encoded in the filename

        parsed_data = self._parse_data(data_file)
        self.regions = parsed_data['regions']
        self.parties = parsed_data['parties']
        self.electoral_system = electoral_systems.System(name='dHondt', level=2, threshold=3)
        self.colors = spain_colors
        self._build_region_tree()

        super(Spain_Election, self).__init__(country=spain_country, date=date)

    def _build_region_tree(self):
        self.regions[0]['Spain'].subregions = self.regions[1].values()
        for region_name, region_value in self.regions[2].items():
            if hasattr(self.regions[1][spain_ccaa_and_provinces[region_name]], 'subregions'):
                self.regions[1][spain_ccaa_and_provinces[region_name]].subregions.append(region_value)
            else:
                self.regions[1][spain_ccaa_and_provinces[region_name]].subregions = [region_value]


class Spain_2019_11(Spain_Election):
    """
    Class representing the elections that were held in Spain on 10-11-2019.
    """
    def __init__(self):
        filename = 'data/Spain/election_data_2019-11-10.pkl'
        filename = os.path.join(os.path.dirname(__file__), filename)
        super(Spain_2019_11, self).__init__(data_file=filename)
        return


class Spain_2019_04(Spain_Election):
    """
    Class representing the elections that were held in Spain on 04-28-2019.
    """
    def __init__(self):
        filename = 'data/Spain/election_data_2019-04-28.pkl'
        filename = os.path.join(os.path.dirname(__file__), filename)
        super(Spain_2019_04, self).__init__(data_file=filename)
        return


class Spain_2016_06(Spain_Election):
    """
    Class representing the elections that were held in Spain on 26-06-2016.
    """
    def __init__(self):
        filename = 'data/Spain/election_data_2016-06-26.pkl'
        filename = os.path.join(os.path.dirname(__file__), filename)
        super(Spain_2016_06, self).__init__(data_file=filename)
        return


class Spain_2015_12(Spain_Election):
    """
    Class representing the elections that were held in Spain on 20-12-2015.
    """
    def __init__(self):
        filename = 'data/Spain/election_data_2015-12-20.pkl'
        filename = os.path.join(os.path.dirname(__file__), filename)
        super(Spain_2015_12, self).__init__(data_file=filename)
        return


class Spain_2011_11(Spain_Election):
    """
    Class representing the elections that were held in Spain on 20-11-2011.
    """
    def __init__(self):
        filename = 'data/Spain/election_data_2011-11-20.pkl'
        filename = os.path.join(os.path.dirname(__file__), filename)
        super(Spain_2011_11, self).__init__(data_file=filename)
        return


class Spain_2008_03(Spain_Election):
    """
    Class representing the elections that were held in Spain on 09-03-2008.
    """
    def __init__(self):
        filename = 'data/Spain/election_data_2008-03-09.pkl'
        filename = os.path.join(os.path.dirname(__file__), filename)
        super(Spain_2008_03, self).__init__(data_file=filename)
        return


class Spain_2004_03(Spain_Election):
    """
    Class representing the elections that were held in Spain on 14-03-2004.
    """
    def __init__(self):
        filename = 'data/Spain/election_data_2004-03-14.pkl'
        filename = os.path.join(os.path.dirname(__file__), filename)
        super(Spain_2004_03, self).__init__(data_file=filename)
        return


class Spain_2000_03(Spain_Election):
    """
    Class representing the elections that were held in Spain on 12-03-2000.
    """
    def __init__(self):
        filename = 'data/Spain/election_data_2000-03-12.pkl'
        filename = os.path.join(os.path.dirname(__file__), filename)
        super(Spain_2000_03, self).__init__(data_file=filename)
        return


#######
# USA #
#######

# https://en.wikipedia.org/wiki/Category:United_States_political_party_color_templates
usa_colors = {
    'Democrat': '#3333FF',
    'Republican': '#E81B23',
    'Libertarian': '#FED105',
    'Conservative': '#FF8C00',
    'Working Families': '#F598E2',
    'Green': '#17AA5C',
    'Constitution': '#A356DE',
}


class USA_2020(Election):
    def __init__(self):
        data_file = 'data/USA/election_data.pkl'
        data_file = os.path.join(os.path.dirname(__file__), data_file)
        parsed_data = self._parse_data(data_file)
        self.regions = parsed_data['regions']
        self.parties = parsed_data['parties']
        self.electoral_system = electoral_systems.System(name='dHondt', level=2, threshold=0)
        self.colors = usa_colors
        self._build_region_tree()

        super(USA_2020, self).__init__(country=countries.USA(), date='2020')

    def _build_region_tree(self):
        self.regions[0]['USA'].subregions = self.regions[1].values()
        for region_name, region_value in self.regions[2].items():
            if hasattr(self.regions[1][region_name.split('_')[0]], 'subregions'):
                self.regions[1][region_name.split('_')[0]].subregions.append(region_value)
            else:
                self.regions[1][region_name.split('_')[0]].subregions = [region_value]
