from collections import Counter
import geopandas as gpd
import json
import pandas as pd
import pickle


def preprocess_geojsons():
    # Level 2
    districts_gdf = gpd.read_file("districts114/districtShapes/districts114.shp")
    districts_gdf = districts_gdf[districts_gdf['STATENAME'] != 'District Of Columbia']
    districts_gdf['name'] = districts_gdf['STATENAME'] + '_' + districts_gdf['DISTRICT']
    districts_gdf['geometry'] = districts_gdf['geometry'].apply(lambda x: x.simplify(0.2))
    map_geojson = json.loads(districts_gdf['geometry'].to_json())
    for i in range(len(map_geojson['features'])):
        map_geojson['features'][i]['id'] = districts_gdf['name'].iloc[i]
    with open('../../app/data/USA/level_2.geojson', 'w') as f:
        json.dump(map_geojson, f)

    # Level 1
    states_gdf = gpd.read_file("states/s_11au16.shp")
    good_states = set()
    for state in pd.unique(states_gdf['NAME']):
        good_states.add(state)
    states_gdf = states_gdf[states_gdf['NAME'].isin(good_states)]
    states_gdf['geometry'] = states_gdf['geometry'].apply(lambda x: x.simplify(0.2))
    map_geojson = json.loads(states_gdf['geometry'].to_json())
    for i in range(len(map_geojson['features'])):
        map_geojson['features'][i]['id'] = states_gdf['NAME'].iloc[i]
    with open('../../app/data/USA/level_1.geojson', 'w') as f:
        json.dump(map_geojson, f)

    # Level 0
    countries_gdf = gpd.read_file('../countries.geojson')
    usa_geojson = countries_gdf.loc[countries_gdf['ADMIN'] == 'United States of America']['geometry'].to_json()
    usa_geojson = json.loads(usa_geojson)
    usa_geojson['features'][0]['id'] = 'USA'
    with open('../../app/data/USA/level_0.geojson', 'w') as f:
        json.dump(usa_geojson, f)


def preprocess_electoral_data():
    votes_df = pd.read_csv('1976-2020-house.csv', encoding="ISO-8859-1")

    # Select only the 2020 elections for now
    votes_df = votes_df[(votes_df['year'] == 2020)]

    columns_to_keep = ['state', 'district', 'party', 'candidatevotes', 'totalvotes']
    votes_df = votes_df[columns_to_keep]

    # Drop 'District of Columbia'
    votes_df = votes_df[votes_df.state != 'DISTRICT OF COLUMBIA']

    # Capitalize names
    votes_df['state'] = votes_df['state'].str.title()
    votes_df['party'] = votes_df['party'].str.capitalize()

    parties = list(pd.unique(votes_df['party']))

    level_0_data = {
        'region_name': 'USA',
        'level': 0,
        'census': 0,
        'n_seats': 0,
        'votes': Counter(),
        'nota': 0,
        'split_votes': 0,
    }

    level_1_regions = list(pd.unique(votes_df['state']))
    level_1_data = {}
    for region in level_1_regions:
        level_1_data[region] = {
            'region_name': region,
            'level': 1,
            'census': 0,
            'n_seats': 0,
            'votes': Counter(),
            'nota': 0,
            'split_votes': 0,
        }

    level_2_data = {}
    votes_df['name'] = votes_df['state'] + '_' + votes_df['district'].astype(str)
    for district_name in pd.unique(votes_df['name']):
        district_df = votes_df[votes_df['name'] == district_name]
        census = district_df['totalvotes'].iloc[0]
        votes = {}
        for idx, row in district_df.iterrows():
            votes[row['party']] = row['candidatevotes']
        nota = census - sum(votes.values())

        if district_name == 'Florida_25':  # There's no data; only that there's Republican party
            census = 1
            votes = {'Republican': 1}
            nota = 0

        level_2_data[district_name] = {
            'region_name': district_name,
            'level': 2,
            'census': census,
            'n_seats': 1,
            'votes': votes,
            'nota': nota,
            'split_votes': 0,
        }

        # Add level 1 data
        lvl1_name = district_df['state'].iloc[0]
        level_1_data[lvl1_name]['census'] += census
        level_1_data[lvl1_name]['n_seats'] += 1
        level_1_data[lvl1_name]['votes'] += votes
        level_1_data[lvl1_name]['nota'] += nota

        # Add level 0 data
        level_0_data['census'] += census
        level_0_data['n_seats'] += 1
        level_0_data['votes'] += votes
        level_0_data['nota'] += nota

    result = {
        'parties': parties,
        'data': {
            0: level_0_data,
            1: level_1_data,
            2: level_2_data
        }
    }

    output_filename = '../../app/data/USA/election_data'
    output_filename += '.pkl'
    with open(output_filename, "wb") as f:
        pickle.dump(result, f, protocol=5)


if __name__ == "__main__":
    preprocess_geojsons()
    # preprocess_electoral_data()
