import glob
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point, Polygon

def convert_time(data):
    data['realtime'] = pd.to_datetime(data['pingtimestamp'], unit = 's')
    return data

def plot(df):
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

def main():
    df_list = []
    for file in glob.glob("dataset/part-*.parquet"):
        df_ = pd.read_parquet(file, engine = 'pyarrow')
        df_list.append(df_)

    df = pd.concat(df_list, ignore_index=True)
    print(df.shape)
    convert_time(df)
    df.drop(columns = ["pingtimestamp"], inplace=True)
    df = df.sort_values(by=['trj_id', 'realtime'], ascending=True)

    #try
    df = df[df["trj_id"] == "10"]
    plot(df)

main()