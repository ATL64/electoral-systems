from collections import Counter
import geopandas
import json
import pandas as pd
import pickle


def preprocess_geojsons():
    # Level 2
    gdf = geopandas.read_file('provincias-espanolas.geojson')
    map_geojson = json.loads(gdf['geometry'].to_json())
    for i in range(len(map_geojson['features'])):
        map_geojson['features'][i]['id'] = gdf['provincia'][i]
    with open('../../app/data/Spain/level_2.geojson', 'w') as f:
        json.dump(map_geojson, f)

    # Level 1
    gdf = geopandas.read_file('spain-comunidad-with-canary-islands.json')
    map_geojson = json.loads(gdf['geometry'].to_json())
    for i in range(len(map_geojson['features'])):
        map_geojson['features'][i]['id'] = gdf['NAME_1'][i]
    with open('../../app/data/Spain/level_1.geojson', 'w') as f:
        json.dump(map_geojson, f)

    # Level 0
    countries_gdf = geopandas.read_file('../countries.geojson')
    spain_geojson = countries_gdf.loc[countries_gdf['ADMIN'] == 'Spain']['geometry'].to_json()
    spain_geojson = json.loads(spain_geojson)
    spain_geojson['features'][0]['id'] = 'Spain'
    with open('../../app/data/Spain/level_0.geojson', 'w') as f:
        json.dump(spain_geojson, f)


def preprocess_electoral_data(filename, date, df_cols, df_header, parties_cols, parties_header):
    df = pd.read_excel(filename,
                       header=df_header,
                       nrows=52,
                       usecols=df_cols)
    parties = pd.read_excel(filename,
                            header=parties_header,
                            usecols=parties_cols,
                            nrows=1)

    parties = parties[parties.columns[::2]]
    parties = parties.loc[0].values.flatten().tolist()
    parties = [x.strip() for x in parties]

    level_0_data = {
        'region_name': 'Spain',
        'level': 0,
        'census': 0,
        'n_seats': 0,
        'votes': Counter(),
        'nota': 0,
        'split_votes': 0,
    }
    level_1_regions = [
        'Andalucía',
        'Aragón',
        'Cantabria',
        'Castilla y León',
        'Castilla-La Mancha',
        'Cataluña',
        'Ceuta y Melilla',
        'Comunidad de Madrid',
        'Comunidad Foral de Navarra',
        'Comunidad Valenciana',
        'Extremadura',
        'Galicia',
        'Islas Baleares',
        'Islas Canarias',
        'La Rioja',
        'País Vasco',
        'Principado de Asturias',
        'Región de Murcia',
    ]
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
        elif 'Balears' in region_name:
            region_name = 'Illes Balears'
        elif 'Palmas' in region_name:
            region_name = 'Las Palmas'
        elif 'Coruña' in region_name:
            region_name = 'A Coruña'
        elif 'Rioja' in region_name:
            region_name = 'La Rioja'
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

        level_2_data[region_name] = {
            'region_name': region_name,
            'level': 2,
            'census': census,
            'n_seats': n_seats,
            'votes': votes,
            'nota': nota,
            'split_votes': split_votes,
        }

        # Add level 1 data
        lvl1_name = row['Nombre de Comunidad'].strip()
        if 'Ceuta' in lvl1_name or 'Melilla' in lvl1_name:  # Ciudad de Ceuta, Ciudad de Melilla
            lvl1_name = 'Ceuta y Melilla'
        elif lvl1_name == 'Castilla - La Mancha':
            lvl1_name = 'Castilla-La Mancha'
        elif 'Balears' in lvl1_name:
            lvl1_name = 'Islas Baleares'
        elif lvl1_name.startswith('Comunitat'):
            lvl1_name = 'Comunidad Valenciana'
        elif lvl1_name.startswith('Canarias'):
            lvl1_name = 'Islas Canarias'
        elif lvl1_name.startswith('Asturias'):
            lvl1_name = 'Principado de Asturias'
        elif lvl1_name.startswith('Madrid'):
            lvl1_name = 'Comunidad de Madrid'
        elif lvl1_name.startswith('Navarra'):
            lvl1_name = 'Comunidad Foral de Navarra'
        elif lvl1_name.startswith('Murcia'):
            lvl1_name = 'Región de Murcia'
        elif lvl1_name.startswith('Rioja'):
            lvl1_name = 'La Rioja'
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

    result = {
        'parties': parties,
        'data': {
            0: level_0_data,
            1: level_1_data,
            2: level_2_data
        }
    }

    output_filename = '../../app/data/Spain/election_data'
    output_filename += date
    output_filename += '.pkl'
    with open(output_filename, "wb") as f:
        pickle.dump(result, f, protocol=5)


if __name__ == "__main__":
    preprocess_geojsons()
    # preprocess_electoral_data('PROV_02_201911_1.xlsx', '_2019-11-10', 'A:ET', 5, 'Q:ET', 3)
    # preprocess_electoral_data('PROV_02_201904_1.xlsx', '_2019-04-28', 'A:ET', 5, 'Q:ET', 3)
    # preprocess_electoral_data('PROV_02_201606_1.xlsx', '_2016-06-26', 'A:DN', 5, 'Q:DN', 3)
    # preprocess_electoral_data('PROV_02_201512_1.xlsx', '_2015-12-20', 'A:DX', 6, 'Q:DX', 4)
    # preprocess_electoral_data('PROV_02_201111_1.xlsx', '_2011-11-20', 'A:EJ', 5, 'Q:EJ', 3)
    # preprocess_electoral_data('PROV_02_200803_1.xlsx', '_2008-03-09', 'A:HC', 5, 'P:HC', 3)
    # preprocess_electoral_data('PROV_02_200403_1.xlsx', '_2004-03-14', 'A:GY', 5, 'P:GY', 3)
    # preprocess_electoral_data('PROV_02_200003_1.xlsx', '_2000-03-12', 'A:HA', 5, 'P:HA', 3)
