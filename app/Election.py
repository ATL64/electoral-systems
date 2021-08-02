from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from datetime import datetime
import pandas as pd
import pickle

import Countries
from Regions import Electoral_Region

class Election(ABC):
    def __init__(self, country: Countries.Country, date: str = None):
        self.date = date
        self.country = country
        return

    @property
    @abstractmethod
    def regions(self):
        """
        A list of items of the class Regions.Electoral_Regions, containing all
        the information of a particular election.
        """
        pass

    @property
    @abstractmethod
    def parties(self):
        """
        A list of the parties taking part in the election.
        """
        pass

    @property
    @abstractmethod
    def electoral_system(self):
        """
        A dictionary containing the following information about the election:
        - Name of the electoral system ('name')
        - The region level used ('level')
        - The minimum threshold for a party to get seats ('threshold')
        """
        pass

    def get_compare_metrics(self, system_1, system_2):
        seat_diff = {}
        seats_won = Counter()
        final_results_1 = Counter()
        final_results_2 = Counter()

        regions = self.regions()

        for region in regions[system_1['level']]:
            final_results_1 += region.compute_election_result(system_1)
        for region in regions[system_2['level']]:
            final_results_2 += region.compute_election_result(system_2)

        if system_1['level']==system_2['level']:
            for region in regions[system_1['level']]:
                seat_diff[region.name] = 0
                system_1_votes = region.compute_election_result(system_1)
                system_2_votes = region.compute_election_result(system_2)
                parties = set(system_1_votes.keys()).union(system_2_votes.keys())
                for p in parties:
                    if p in system_1_votes and p not in system_2_votes:
                        seat_diff[region.name] += system_1_votes[p]
                        seats_won[p] += system_1_votes[p]
                    elif p in system_2_votes and p not in system_1_votes:
                        seats_won[p] -= system_2_votes[p]
                    elif system_1_votes[p]>system_2_votes[p]:
                        seat_diff[region.name] += system_1_votes[p] - system_2_votes[p]
                        seats_won[p] += system_1_votes[p] - system_2_votes[p]
                    else:
                        seats_won[p] -= system_2_votes[p] - system_1_votes[p]

        elif system_1['level']==0 or system_2['level']==0:
            seat_diff[self.country.name] = 0
            if system_1['level']==0:
                system_1_votes = regions[0][0].compute_election_result(system_1)
                system_2_votes = Counter()
                for region in regions[system_2['level']]:
                    system_2_votes += region.compute_election_result(system_2)
            else:
                system_2_votes = regions[0][0].compute_election_result(system_2)
                system_1_votes = Counter()
                for region in regions[system_1['level']]:
                    system_1_votes += region.compute_election_result(system_1)

            parties = set(system_1_votes.keys()).union(system_2_votes.keys())
            for p in parties:
                if p in system_1_votes and p not in system_2_votes:
                    seat_diff[self.country.name] += system_1_votes[p]
                    seats_won[p] += system_1_votes[p]
                elif p in system_2_votes and p not in system_1_votes:
                    seats_won[p] -= system_2_votes[p]
                elif system_1_votes[p]>system_2_votes[p]:
                    seat_diff[self.country.name] += system_1_votes[p] - system_2_votes[p]
                    seats_won[p] += system_1_votes[p] - system_2_votes[p]
                else:
                    seats_won[p] -= system_2_votes[p] - system_1_votes[p]

        elif system_1['level']==1:
            system_2_region_votes = defaultdict(Counter)
            for region in regions[system_2['level']]:
                votes = region.compute_election_result(system_2)
                system_2_region_votes[self.superregion[region.name]] += votes

            for region in regions[system_1['level']]:
                seat_diff[region.name] = 0
                system_1_votes = region.compute_election_result(system_1)
                system_2_votes = system_2_region_votes[region.name]
                parties = set(system_1_votes.keys()).union(system_2_votes.keys())
                for p in parties:
                    if p in system_1_votes and p not in system_2_votes:
                        seat_diff[region.name] += system_1_votes[p]
                        seats_won[p] += system_1_votes[p]
                    elif p in system_2_votes and p not in system_1_votes:
                        seats_won[p] -= system_2_votes[p]
                    elif system_1_votes[p]>system_2_votes[p]:
                        seat_diff[region.name] += system_1_votes[p] - system_2_votes[p]
                        seats_won[p] += system_1_votes[p] - system_2_votes[p]
                    else:
                        seats_won[p] -= system_2_votes[p] - system_1_votes[p]

        elif system_2['level']==1:
            system_1_region_votes = defaultdict(Counter)
            for region in regions[system_1['level']]:
                votes = region.compute_election_result(system_1)
                system_1_region_votes[self.superregion[region.name]] += votes

            for region in regions[system_2['level']]:
                seat_diff[region.name] = 0
                system_2_votes = region.compute_election_result(system_2)
                system_1_votes = system_1_region_votes[region.name]
                parties = set(system_1_votes.keys()).union(system_2_votes.keys())
                for p in parties:
                    if p in system_1_votes and p not in system_2_votes:
                        seat_diff[region.name] += system_1_votes[p]
                        seats_won[p] += system_1_votes[p]
                    elif p in system_2_votes and p not in system_1_votes:
                        seats_won[p] -= system_2_votes[p]
                    elif system_1_votes[p]>system_2_votes[p]:
                        seat_diff[region.name] += system_1_votes[p] - system_2_votes[p]
                        seats_won[p] += system_1_votes[p] - system_2_votes[p]
                    else:
                        seats_won[p] -= system_2_votes[p] - system_1_votes[p]

        return {'seat_diff': seat_diff, 'seats_won': seats_won, 'final_results_1': final_results_1, 'final_results_2': final_results_2}

    def get_single_metrics(self, system_1):
        lost_votes = {}
        lost_votes_percentage = {}
        party_lost_votes = Counter()

        regions = self.regions()
        for region in regions[system_1['level']]:
            system_votes = region.compute_election_result(system_1)
            parties = set(system_votes)
            # Compute lost votes
            lost_votes[region.name] = 0
            for p in region.votes:
                if p not in system_votes:
                    lost_votes[region.name] += region.votes[p]
                    party_lost_votes[p] += region.votes[p]
            lost_votes_percentage[region.name] = lost_votes[region.name] / sum(region.votes.values())

        return {'lost_votes_percentage': lost_votes_percentage, 'party_lost_votes': party_lost_votes}


class Spain_Election(Election):
    def __init__(self, data_file: str):
        date = data_file.split('_')[-1].split('.')[0]
        super(Spain_Election, self).__init__(country=Countries.Spain(), date=date)

        parsed_data = self.parse_data(data_file)
        self._regions = parsed_data['regions']
        self._parties = parsed_data['parties']

        # See https://en.wikipedia.org/wiki/Category:Spain_political_party_colour_templates
        self.colors = {
            'AMAIUR': '#087178',
            'BNG': '#ADCFEF',
            'B.N.G.': '#ADCFEF',
            'NÓS': '#ADCFEF',
            'CC': '#FFD700',
            'CC-PNC': '#FFD700',
            'CCa-PNC-NC': '#FFD700',
            'CCa-PNC': '#FFD700',
            'CC-NC-PNC': '#FFD700',
            'CDC': '#18307B',
            'CHA': '#008A21', # Chunta Aragonesista, 2004
            'CIU': '#18307B',
            'CiU': '#18307B',
            'DL': '#18307B',
            'Cs': '#EB6109',
            "C's": '#EB6109',
            'COMPROMÍS 2019': '#DA5C31',
            'COMPROMÍS-Q': '#DA5C31',
            'CUP-PR': '#FFED00',
            'EA': '#77AC1C', # Eusko-Alkartasuna, 2004
            'EAJ-PNV': '#4AAE4A',
            'ECP-GUANYEM EL CANVI': '#5A205A',
            'ECP': '#5A205A',
            'EH Bildu': '#B5CF18',
            'EN COMÚ': '#5A205A',
            'EQUO': '#8ABA18',
            'ERC': '#8ABA18',
            'ERC-CATSI': '#FFB232',
            'ERC-SOBIRANISTES': '#FFB232',
            'ESQUERRA': '#FFB232',
            'FAC': '#10286B',
            'IC-V': '#4E9E41', # Iniciativa per Catalunya, 2000
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
            'NA+': '#819DA3',
            'NC-CCN': '#BAF73E',
            'Nca': '#639E42',
            'PA': '#005931', # Partido Andalucista, 2004
            'PACMA': '#ADBE18',
            'PP': '#007FFF',
            'P.P.': '#007FFF',
            'PRC': '#C2CE0C',
            'P.R.C.': '#C2CE0C',
            'PSM-EN,EU,EV,ER': '#FF9933', # Progressistes per les Illes Balears, 2004
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
            'UPL': '#B41062', # Unión del Pueblo Leonés, 2000
            'UPYD': '#E9008C',
            'UPyD': '#E9008C',
            'UV': '#1F4473', # Unió Valenciana, 2000
            'VOX': '#63BE21',
            '¡TERUEL EXISTE!': '#037252',
        }

        self.superregion = {}
        for x in ['Almería', 'Cádiz', 'Córdoba', 'Granada', 'Huelva', 'Jaén', 'Málaga', 'Sevilla']:
            self.superregion[x] = 'Andalucía'
        for x in ['Huesca', 'Teruel', 'Zaragoza']:
            self.superregion[x] = 'Aragón'
        self.superregion['Cantabria'] = 'Cantabria'
        for x in ['Ávila', 'Burgos', 'León', 'Palencia', 'Salamanca', 'Segovia', 'Soria', 'Valladolid', 'Zamora']:
            self.superregion[x] = 'Castilla y León'
        for x in ['Albacete', 'Ciudad Real', 'Cuenca', 'Guadalajara', 'Toledo']:
            self.superregion[x] = 'Castilla-La Mancha'
        for x in ['Barcelona', 'Girona', 'Lleida', 'Tarragona']:
            self.superregion[x] = 'Cataluña'
        self.superregion['Ceuta'] = 'Ceuta y Melilla'
        self.superregion['Melilla'] = 'Ceuta y Melilla'
        self.superregion['Madrid'] = 'Comunidad de Madrid'
        self.superregion['Navarra'] = 'Comunidad Foral de Navarra'
        for x in ['Alacant', 'Castelló', 'València']:
            self.superregion[x] = 'Comunidad Valenciana'
        self.superregion['Badajoz'] = 'Extremadura'
        self.superregion['Cáceres'] = 'Extremadura'
        for x in ['A Coruña', 'Lugo', 'Ourense', 'Pontevedra']:
            self.superregion[x] = 'Galicia'
        self.superregion['Illes Balears'] = 'Islas Baleares'
        self.superregion['Las Palmas'] = 'Islas Canarias'
        self.superregion['Santa Cruz de Tenerife'] = 'Islas Canarias'
        self.superregion['La Rioja'] = 'La Rioja'
        for x in ['Araba', 'Bizkaia', 'Gipuzcoa']:
            self.superregion[x] = 'País Vasco'
        self.superregion['Asturias'] = 'Principado de Asturias'
        self.superregion['Murcia'] = 'Región de Murcia'

    def parse_data(self, filename):
        with open(filename, 'rb') as f:
            data = pickle.load(f)

        level_0_electoral_region = Electoral_Region(
            data['data'][0]['region_name'],
            data['data'][0]['level'],
            data['data'][0]['census'],
            data['data'][0]['n_seats'],
            data['data'][0]['votes'],
            data['data'][0]['nota'],
            data['data'][0]['split_votes'],
        )

        level_1_electoral_regions = []
        for region, results in data['data'][1].items():
            level_1_electoral_regions.append(Electoral_Region(
                results['region_name'],
                results['level'],
                results['census'],
                results['n_seats'],
                results['votes'],
                results['nota'],
                results['split_votes'],
            ))

        level_2_electoral_regions = []
        for region, results in data['data'][2].items():
            level_2_electoral_regions.append(Electoral_Region(
                results['region_name'],
                results['level'],
                results['census'],
                results['n_seats'],
                results['votes'],
                results['nota'],
                results['split_votes'],
            ))

        electoral_regions = {
            0: [level_0_electoral_region],
            1: level_1_electoral_regions,
            2: level_2_electoral_regions,
        }
        return {'parties': data['parties'], 'regions': electoral_regions}

    def regions(self):
        return self._regions

    def parties(self):
        return self._parties

    def electoral_system(self):
        return {'name': 'dHondt', 'threshold': 0.03, 'level': 2}

class Spain_2019_11(Spain_Election):
    def __init__(self):
        super(Spain_2019_11, self).__init__(data_file='data/Spain/election_data_2019-11-10.pkl')
        return

class Spain_2019_04(Spain_Election):
    def __init__(self):
        super(Spain_2019_04, self).__init__(data_file='data/Spain/election_data_2019-04-28.pkl')
        return


class Spain_2016_06(Spain_Election):
    def __init__(self):
        super(Spain_2016_06, self).__init__(data_file='data/Spain/election_data_2016-06-26.pkl')
        return

class Spain_2015_12(Spain_Election):
    def __init__(self):
        super(Spain_2015_12, self).__init__(data_file='data/Spain/election_data_2015-12-20.pkl')
        return

class Spain_2011_11(Spain_Election):
    def __init__(self):
        super(Spain_2011_11, self).__init__(data_file='data/Spain/election_data_2011-11-20.pkl')
        return

class Spain_2008_03(Spain_Election):
    def __init__(self):
        super(Spain_2008_03, self).__init__(data_file='data/Spain/election_data_2008-03-09.pkl')
        return

class Spain_2008_03(Spain_Election):
    def __init__(self):
        super(Spain_2008_03, self).__init__(data_file='data/Spain/election_data_2008-03-09.pkl')
        return

class Spain_2004_03(Spain_Election):
    def __init__(self):
        super(Spain_2004_03, self).__init__(data_file='data/Spain/election_data_2004-03-14.pkl')
        return

class Spain_2000_03(Spain_Election):
    def __init__(self):
        super(Spain_2000_03, self).__init__(data_file='data/Spain/election_data_2000-03-12.pkl')
        return
