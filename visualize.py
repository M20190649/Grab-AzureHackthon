import osmnx as ox
import geopandas as gpd
import pandas as pd
import networkx as nx

def convert_time(data):
    data['realtime'] = pd.to_datetime(data['pingtimestamp'], unit = 's').dt.tz_localize('Asia/Singapore')
    return data

def plot_route(map, ori, dest):
    origin = ox.get_nearest_node(sg, ori)
    destination = ox.get_nearest_node(sg, dest)
    route = nx.shortest_path(sg, origin, destination, weight = 'length')
    ox.plot_graph_route(sg, route, node_size=0)

data = pd.read_parquet('dataset/part-00000-8bbff892-97d2-4011-9961-703e38972569.c000.snappy.parquet', engine='pyarrow')
convert_time(data)
data.sort_values(by=['trj_id', 'realtime'], ascending=True)

sg = ox.graph_from_place('Singapore', network_type ='drive')
ox.plot_graph(sg)


plot_route(sg, ori = (1.301581, 103.799431), dest = (1.301523,  103.801057))

