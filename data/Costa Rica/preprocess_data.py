from collections import Counter
import geopandas as gpd
import json
import pandas as pd
import pickle

region_seats = {
    'Alajuela': 11,
    'Cartago': 7,
    'Guanacaste': 4,
    'Heredia': 6,
    'Limón': 5,
    'Puntarenas': 5,
    'San José': 19,
}

df = pd.read_csv('2018/Alajuela.csv')


def preprocess_geojsons():
    # Level 1
    gdf = gpd.read_file("cri_adm_2020_shp/cri_admbnda_adm1_2020.shp")
    gdf.to_crs("EPSG:4326", inplace=True)
    map_geojson = json.loads(gdf['geometry'].to_json())
    for i in range(len(map_geojson['features'])):
        map_geojson['features'][i]['id'] = gdf['ADM1_ES'].iloc[i]
    with open('../../app/data/Costa Rica/level_1.geojson', 'w') as f:
        json.dump(map_geojson, f)

    # Level 0
    gdf = gpd.read_file("cri_adm_2020_shp/cri_admbnda_adm0_2020.shp")
    gdf.to_crs("EPSG:4326", inplace=True)
    map_geojson = json.loads(gdf['geometry'].to_json())
    for i in range(len(map_geojson['features'])):
        map_geojson['features'][i]['id'] = gdf['ADM0_ES'].iloc[i]
    with open('../../app/data/Costa Rica/level_0.geojson', 'w') as f:
        json.dump(map_geojson, f)


def preprocess_electoral_data():
    level_0_data = {
        'region_name': 'Costa Rica',
        'level': 0,
        'census': 0,
        'n_seats': 0,
        'votes': Counter(),
        'nota': 0,
        'split_votes': 0,
    }
    level_1_data = dict()

    parties = set()

    for region in region_seats:
        df = pd.read_csv('2018/' + region + '.csv')
        df.set_index('Partido político', inplace=True)

        census = int(df.loc['Votos recibidos', 'Votos'].strip().replace('.', ''))
        nota = int(df.loc['Nulos y blancos', 'Votos'].strip().replace('.', ''))

        votes = dict()
        for idx, row in df.iterrows():
            if type(row['%']) == str and len(row['%']) > 0:
                votes[idx] = int(row['Votos'].strip().replace('.', ''))
                parties.add(idx)

        level_1_data[region] = {
            'region_name': region,
            'level': 1,
            'census': census,
            'n_seats': region_seats[region],
            'votes': votes,
            'nota': nota,
            'split_votes': 0,
        }

        level_0_data['census'] += census
        level_0_data['n_seats'] += region_seats[region]
        level_0_data['votes'] += votes
        level_0_data['nota'] += nota

    result = {
        'parties': list(parties),
        'data': {
            0: level_0_data,
            1: level_1_data,
        }
    }

    output_filename = '../../app/data/Costa Rica/election_data'
    output_filename += '.pkl'
    with open(output_filename, "wb") as f:
        pickle.dump(result, f, protocol=5)


if __name__ == "__main__":
    preprocess_geojsons()
    preprocess_electoral_data()
