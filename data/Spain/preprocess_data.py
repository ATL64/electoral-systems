import geopandas
import json
import pickle

def preprocess_level_2_regions():
    # level 2 == Provincias
    gdf = geopandas.read_file('provincias-espanolas.geojson')

    map_geojson = json.loads(gdf['geometry'].to_json())
    for i in range(len(map_geojson['features'])):
        map_geojson['features'][i]['id'] = gdf['provincia'][i]

    regions = {}
    for idx, row in gdf.iterrows():
        regions[row['codigo']] = row['provincia']

    result = {
        'geojson': map_geojson,
        'regions': regions
    }
    
    with open('../../app/data/Spain/regions_level_2.pkl',"wb") as f:
        pickle.dump(result, f, protocol=5)

    return

def preprocess_level_1_regions():
    # level 1 == Comunidades autónomas
    gdf = geopandas.read_file('spain-comunidad-with-canary-islands.json')
    
    map_geojson = json.loads(gdf['geometry'].to_json())
    for i in range(len(map_geojson['features'])):
        map_geojson['features'][i]['id'] = gdf['NAME_1'][i]
        
    regions = {}
    for idx, row in gdf.iterrows():
        regions[idx] = row['NAME_1']
        
    result = {
        'geojson': map_geojson,
        'regions': regions
    }
    
    with open('../../app/data/Spain/regions_level_1.pkl',"wb") as f:
        pickle.dump(result, f, protocol=5)

    return

if __name__=="__main__":
    #preprocess_level_2_regions()
    preprocess_level_1_regions()
