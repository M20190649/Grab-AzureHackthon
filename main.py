import glob
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point, Polygon
from os import path
# import osmnx as ox
# import networkx as nx
from collections import defaultdict
from geojson import MultiPoint, LineString, Feature, FeatureCollection, dump
import requests

df_list = []
geometryJSON = []
trj_coordinate = defaultdict(list)
seen = defaultdict(int)

mapmatch_enable = True

def summary(df):
    trajectories = list(df['trj_id'])
    for trj in trajectories:
        seen[trj] += 1
    return seen

def convert_time(data):
    data['realtime'] = pd.to_datetime(data['pingtimestamp'], unit = 's')
    return data

def plot(df):
    # map_ = ox.graph_from_place('Singapore', network_type ='drive')
    # ox.save_graph_shapefile(map_, filename = "Singapore")
    # sg = ox.load_graphml('a.graphml')
    # ox.plot_graph(sg,show=False)
    
    #Using list comprehension, specify the “Longitude” column before the “Latitude” column
    geometry = [Point(xy) for xy in zip(df["rawlng"], df["rawlat"])]
    # CRS: coordinate reference system
    crs = {'init' : 'EPSG:4326'}
    geo_df = gpd.GeoDataFrame(df, crs = crs, geometry = geometry)
    fig, ax = plt.subplots(figsize = (8,6))
    plt.scatter(geo_df.rawlng, geo_df.rawlat, s = 3, c='red', label = "trj_10")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend(loc='best')
    plt.title("Singapore")
    plt.show()

def map_matching(geometry):
    geo_string = []
    distance = 0

    for geo in geometry:
        geo_ = ','.join([str(elem) for elem in geo])
        geo_string.append(geo_)
    
    list_geometry = ';'.join([str(elem) for elem in geo_string])
    url = 'http://ivolab:5000/match/v1/driving/' + list_geometry
    payload = {"steps": "false", "geometries": "geojson",
               "overview": "full", "annotations": "false", "tidy": "true"}

    response = requests.get(url, params = payload)
    # mapmatched_geopoints = response.json()['matchings'][0]['geometry']
    print(response.url)

    concat_geo = [response.json()['matchings'][i]['geometry']['coordinates']
             for i in range(len(response.json()['matchings']))]
    mapmatched_geopoints = LineString(
        [y for element in concat_geo for y in element])
    
    for i in range(len(response.json()['matchings'])):
        for j in range(len(response.json()['matchings'][i]['legs'])):
            distance += response.json()['matchings'][i]['legs'][j]['distance']
    
    return mapmatched_geopoints, distance

for file in glob.glob("dataset/part-*.parquet"):
    df_ = pd.read_parquet(file, engine = 'pyarrow')
    df_list.append(df_)

df = pd.concat(df_list, ignore_index=True)
print(df.shape)
convert_time(df)
df.drop(columns = ["pingtimestamp"], inplace=True)
df.sort_values(by=['trj_id', 'realtime'], ascending=True, inplace=True)

#plot single trajectories
# data1 = df[df["trj_id"] == "10"]
# plot(data1)

# Generate geojson for MapMatching - QGIS
trajectories = summary(df)

for trj_id, cnt in trajectories.items():

    if path.exists("mapmatched/{}.geojson".format(trj_id)):
        continue
    
    data = df[df["trj_id"] == trj_id]
    trj_coordinate[trj_id] = list(zip(data["rawlng"], data["rawlat"]))
    start, end = data['realtime'].values[0].__str__(), data['realtime'].values[-1].__str__()
    coord = trj_coordinate[trj_id]
    geometry = MultiPoint(coord)
    
    if mapmatch_enable:
        geometry, distance = map_matching(geometry['coordinates'])

    crs = {
        "type": "trajectory",
        "properties": {
            "name": "EPSG:4326"
        }
    }
    prop = {
        "country": "Singapore",
        "distance": distance,
        "origin_time": start,
        "destination_time": end
    }

    # geometryJSON.append(Feature(geometry = geometry, properties = {"country": "Singapore"}))
    geometryJSON = Feature(geometry = geometry, properties = prop)
    geometryJSON = FeatureCollection([geometryJSON], crs = crs)
    
    with open("mapmatched/{}.geojson".format(trj_id), "w") as file:
        dump(geometryJSON, file)
    print("Trajectory {}'s geojson has been generated".format(trj_id))


