from abc import ABC, abstractmethod
from collections import Counter
from datetime import datetime
import pandas as pd

import Countries
from Regions import Electoral_Region

class Election(ABC):
    def __init__(self, date: str, country: Countries.Country):
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
    def level(self):
        """
        The level of the regions of the election.
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

        regions = self.regions()
        # TODO Regions are different if levels are different
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

        return {'seat_diff': seat_diff, 'seats_won': seats_won}

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

class Spain_2019_11(Election):
    def __init__(self):
        super(Spain_2019_11, self).__init__(date=datetime(2019, 11, 10, 0, 0, 0), country=Countries.Spain())
        parsed_data = self.parse_electoral_data()
        self._regions = parsed_data['regions']
        self._parties = parsed_data['parties']
        return

    def parse_electoral_data(self):
        df = pd.read_excel('../data/Spain/PROV_02_201911_1.xlsx',
                           header=5,
                           nrows=52,
                           usecols='A:ET')
        parties = pd.read_excel('../data/Spain/PROV_02_201911_1.xlsx',
                                header=3,
                                usecols='Q:ET',
                                nrows=1)

        parties = parties[parties.columns[::2]]
        parties = parties.loc[0].values.flatten().tolist()

        level_0_data = {
            'region_name': 'Spain',
            'code': 0,
            'level': 0,
            'census': 0,
            'n_seats': 0,
            'votes': Counter(),
            'nota': 0,
            'split_votes': 0,
        }
        level_1_regions = self.country.regions()[1]['regions']
        level_1_data = {}
        for code, region in level_1_regions.items():
            level_1_data[region] = {
                'region_name': region,
                'code': code,
                'level': 1,
                'census': 0,
                'n_seats': 0,
                'votes': Counter(),
                'nota': 0,
                'split_votes': 0,
            }

        level = 2
        electoral_regions = []
        for idx, row in df.iterrows():
            region_name = row['Nombre de Provincia'].strip()
            if region_name.startswith('Alicante'):
                region_name = 'Alacant'
            elif region_name.startswith('Valencia'):
                region_name = 'València'
            elif region_name.startswith('Gipuzkoa'):
                region_name = 'Gipuzcoa'
            elif region_name.startswith('Araba'):
                region_name = 'Araba'
            elif region_name.startswith('Castellón'):
                region_name = 'Castelló'
            else:
                region_name = region_name
            census = row['Total censo electoral']
            votes = {parties[0]: row["Votos"]}
            n_seats = row["Diputados"]
            for i in range(1, len(parties)):
                votes[parties[i]] = row[f"Votos.{i}"]
                n_seats += row[f"Diputados.{i}"]
            nota = row['Votos en blanco']
            split_votes = row['Votos nulos']
            code = row['Código de Provincia']

            # Check that total number of votes makes sense?

            electoral_regions.append(Electoral_Region(region_name, code, level, census, n_seats, votes, nota, split_votes))

            # Add level 1 data
            lvl1_name = row['Nombre de Comunidad'].strip()
            if lvl1_name.startswith('Ciudad'): # Ciudad de Ceuta, Ciudad de Melilla
                lvl1_name = 'Ceuta y Melilla'
            elif lvl1_name == 'Castilla - La Mancha':
                lvl1_name = 'Castilla-La Mancha'
            elif lvl1_name.startswith('Illes'):
                lvl1_name = 'Islas Baleares'
            elif lvl1_name.startswith('Comunitat'):
                lvl1_name = 'Comunidad Valenciana'
            elif lvl1_name.startswith('Canarias'):
                lvl1_name = 'Islas Canarias'
            level_1_data[lvl1_name]['census'] += census
            level_1_data[lvl1_name]['n_seats'] += n_seats
            level_1_data[lvl1_name]['votes'] += votes
            level_1_data[lvl1_name]['nota'] += nota
            level_1_data[lvl1_name]['split_votes'] += split_votes

            # Add level 0 data
            level_0_data['census'] += census
            level_0_data['n_seats'] += n_seats
            level_0_data['votes'] += votes
            level_0_data['nota'] += nota
            level_0_data['split_votes'] += split_votes


        # Level 1 electoral regions
        level_1_electoral_regions = []
        for region, data in level_1_data.items():
            level_1_electoral_regions.append(Electoral_Region(
                data['region_name'],
                data['code'],
                data['level'],
                data['census'],
                data['n_seats'],
                data['votes'],
                data['nota'],
                data['split_votes'],
            ))

        # Level 0 electoral region
        level_0_electoral_region = Electoral_Region(
            'Spain',
            0,
            0,
            level_0_data['census'],
            level_0_data['n_seats'],
            level_0_data['votes'],
            level_0_data['nota'],
            level_0_data['split_votes'],
        )

        return_electoral_regions = {
            0: [level_0_electoral_region],
            1: level_1_electoral_regions,
            2: electoral_regions,
        }
        return {'parties': parties, 'regions': return_electoral_regions}
        #return {'parties': parties, 'regions': electoral_regions}

    def regions(self):
        return self._regions

    def parties(self):
        return self._parties

    def level(self):
        return 2

    def electoral_system(self):
        return {'name': 'dHondt', 'threshold': 0.03, 'level': 2}

class Spain_2019_04(Election):
    def __init__(self):
        super(Spain_2019_04, self).__init__(date=datetime(2019, 4, 28, 0, 0, 0), country=Countries.Spain())
        parsed_data = self.parse_electoral_data()
        self._regions = parsed_data['regions']
        self._parties = parsed_data['parties']
        return

    def parse_electoral_data(self):
        df = pd.read_excel('../data/Spain/PROV_02_201904_1.xlsx',
                           header=5,
                           nrows=52,
                           usecols='A:ET')
        parties = pd.read_excel('../data/Spain/PROV_02_201904_1.xlsx',
                                header=3,
                                usecols='Q:ET',
                                nrows=1)

        parties = parties[parties.columns[::2]]
        parties = parties.loc[0].values.flatten().tolist()

        level = 2
        electoral_regions = []
        for idx, row in df.iterrows():
            region_name = row['Nombre de Provincia'].strip()
            if region_name.startswith('Alicante'):
                region_name = 'Alacant'
            elif region_name.startswith('Valencia'):
                region_name = 'València'
            elif region_name.startswith('Gipuzkoa'):
                region_name = 'Gipuzcoa'
            elif region_name.startswith('Araba'):
                region_name = 'Araba'
            elif region_name.startswith('Castellón'):
                region_name = 'Castelló'
            else:
                region_name = region_name
            census = row['Total censo electoral']
            votes = {parties[0]: row["Votos"]}
            n_seats = row["Diputados"]
            for i in range(1, len(parties)):
                votes[parties[i]] = row[f"Votos.{i}"]
                n_seats += row[f"Diputados.{i}"]
            nota = row['Votos en blanco']
            split_votes = row['Votos nulos']
            code = row['Código de Provincia']

            # Check that total number of votes makes sense?

            electoral_regions.append(Electoral_Region(region_name, code, level, census, n_seats, votes, nota, split_votes))

        return {'parties': parties, 'regions': electoral_regions}

    def regions(self):
        return self._regions

    def parties(self):
        return self._parties

    def level(self):
        return 2

    def electoral_system(self):
        return {'name': 'dHondt', 'threshold': 0.03, 'level': 2}

class Spain_2016_06(Election):
    def __init__(self):
        super(Spain_2016_06, self).__init__(date=datetime(2016, 6, 16, 0, 0, 0), country=Countries.Spain())
        parsed_data = self.parse_electoral_data()
        self._regions = parsed_data['regions']
        self._parties = parsed_data['parties']
        return

    def parse_electoral_data(self):
        df = pd.read_excel('../data/Spain/PROV_02_201606_1.xlsx',
                           header=5,
                           nrows=52,
                           usecols='A:DN')
        parties = pd.read_excel('../data/Spain/PROV_02_201606_1.xlsx',
                                header=3,
                                usecols='Q:DN',
                                nrows=1)

        parties = parties[parties.columns[::2]]
        parties = parties.loc[0].values.flatten().tolist()

        level = 2
        electoral_regions = []
        for idx, row in df.iterrows():
            region_name = row['Nombre de Provincia'].strip()
            if region_name.startswith('Alicante'):
                region_name = 'Alacant'
            elif region_name.startswith('Valencia'):
                region_name = 'València'
            elif region_name.startswith('Gipuzkoa'):
                region_name = 'Gipuzcoa'
            elif region_name.startswith('Araba'):
                region_name = 'Araba'
            elif region_name.startswith('Castellón'):
                region_name = 'Castelló'
            else:
                region_name = region_name
            census = row['Total censo electoral']
            votes = {parties[0]: row["Votos"]}
            n_seats = row["Diputados"]
            for i in range(1, len(parties)):
                votes[parties[i]] = row[f"Votos.{i}"]
                n_seats += row[f"Diputados.{i}"]
            nota = row['Votos en blanco']
            split_votes = row['Votos nulos']
            code = row['Código de Provincia']

            electoral_regions.append(Electoral_Region(region_name, code, level, census, n_seats, votes, nota, split_votes))

        return {'parties': parties, 'regions': electoral_regions}

    def regions(self):
        return self._regions

    def parties(self):
        return self._parties

    def level(self):
        return 2

    def electoral_system(self):
        return {'name': 'dHondt', 'threshold': 0.03, 'level': 2}
