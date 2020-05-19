import glob
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point, Polygon
from os import path
# import osmnx as ox
# import networkx as nx
from collections import defaultdict
from geojson import MultiPoint, Feature, FeatureCollection, dump

df_list = []
geometryJSON = []
trj_coordinate = defaultdict(list)
seen = defaultdict(int)

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
    crs = {'init' : 'epsg:4326'}
    geo_df = gpd.GeoDataFrame(df, crs = crs, geometry = geometry)
    fig, ax = plt.subplots(figsize = (8,6))
    plt.scatter(geo_df.rawlng, geo_df.rawlat, s = 3, c='red', label = "trj_10")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend(loc='best')
    plt.title("Singapore")
    plt.show()

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

    if path.exists("geopoints/{}.geojson".format(trj_id)):
        continue
    
    data = df[df["trj_id"] == trj_id]
    trj_coordinate[trj_id] = list(zip(data["rawlng"], data["rawlat"]))
    coord = trj_coordinate[trj_id]
    geometry = MultiPoint(coord)
    # geometryJSON.append(Feature(geometry = geometry, properties = {"country": "Singapore"}))
    geometryJSON = Feature(geometry = geometry, properties = {"country": "Singapore"})
        
    with open("geopoints/{}.geojson".format(trj_id), "w") as file:
        dump(geometryJSON, file)
    print("Trajectory {}'s geojson has been generated".format(trj_id))


