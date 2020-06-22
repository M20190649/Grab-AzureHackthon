'''
Source : https://data.gov.sg/dataset/realtime-weather-readings?resource_id=8bd37e06-cdd7-4ca4-9ad8-5754eb70a33d
param: date_time to retrieve the latest available data at particular time
     : date to retrieve all of the readings for that day.
'''
from dateutil import tz
import requests
from datetime import datetime
import pandas as pd
from os import path
import glob
import geojson
from math import radians, degrees, sin, cos, asin, acos, sqrt

def haversine(lat1, lng1, lat2, lng2):
    '''
    calculate the great circle distance for the shortest distance between the coordinate_x with the referenced tower.
    '''
    r = 6371  # in kilometer unit
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    distanceLng = lng2 - lng1
    distanceLat = lat2 - lat1
    a = sin(distanceLat/2)**2 + cos(lat1)*cos(lat2)*sin(distanceLng/2)**2

    return 2*r*asin(sqrt(a))

def nearest_distance(distance_entries, ref):
    return min(distance_entries, key=lambda p: haversine(ref['latitude'], ref['longitude'], p['latitude'], p["longitude"]))

def nearest_time(time_entries, pivot):
    return min(time_entries, key=lambda x: abs(x - pivot))

def convert_dt_(time_string):
    datetime_object = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S+08:00")
    timestamp_object = pd.to_datetime(datetime_object)
    return timestamp_object

def convert_utc_to_local(time_string):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Asia/Singapore')

    # utc = datetime.utcnow()
    utc = datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S')

    # Tell the datetime object that it's in UTC time zone since
    # datetime objects are 'naive' by default
    utc = utc.replace(tzinfo=from_zone)

    # Convert time zone
    local_time = utc.astimezone(to_zone)
    query_time = datetime.strftime(local_time, "%Y-%m-%dT%H:%M:%S")
    return query_time

def rainfall_rate(query_time):
    rainfall = 0
    for x in content['items']:
        if x['timestamp'] == query_time:
            for y in x['readings']:
                if y['station_id'] == device_id:
                    rainfall = y['value']

def get_deviceID(getClosestCoordinate):
    for station in content_station:
        if getClosestCoordinate == station['location']:
            return station['device_id']


def get_rainfall(device_id):
    for rd in content_readings:
        if rd['station_id'] == device_id:
            return rd['value']

for geojsonfile in glob.glob("mapmatched/*.geojson"):

    fn = path.basename(geojsonfile)
    if path.exists("mapmatched_rainfall/{}".format(fn)):
        continue
    
    print("Looking at {}...".format(fn))

    with open(geojsonfile, "r") as f:
        geofile = geojson.load(f)

    ref = {}
    ref['latitude'] = geofile['features'][0]['geometry']['coordinates'][0][0]
    ref['longitude'] = geofile['features'][0]['geometry']['coordinates'][0][1]
    pivot = geofile['features'][0]['properties']['origin_time']
    query_time = convert_utc_to_local(pivot)

    # The dataset is ranging from 8 april - 21 april 2019
    url = 'https://api.data.gov.sg/v1/environment/rainfall'
    payload = {
        "date_time": query_time
    }
    response = requests.get(url, params = payload)
    content = response.json()
    content_station = content['metadata']['stations']
    content_readings = content['items'][0]['readings']

    coordinate = [content_station[i]['location'] for i in range(len(content_station))]

    # ref = {'latitude': 1.3191, 'longitude': 103.8191}
    getClosestCoordinate = nearest_distance(coordinate, ref)

    # dt_ = [i["timestamp"] for i in content['items']]
    # ts_entries = []

    # for dt in dt_:
    #     datetime_object = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S+08:00")
    #     timestamp_object = pd.to_datetime(datetime_object)
    #     ts_entries.append(timestamp_object)

    # query_time = nearest_time(ts_entries, pivot)
    # query_time = query_time.strftime("%Y-%m-%dT%H:%M:%S+08:00")

    device_id = get_deviceID(getClosestCoordinate)
    rainfall = get_rainfall(device_id)

    geofile['features'][0]['properties']['rainfall'] = rainfall

    with open('mapmatched_rainfall/{}'.format(fn), 'w') as f:
        geojson.dump(geofile, f)
        print("[Info]: Dumped geojson with the rainfall")

    # {
    #     "country": country,
    #     "trj_id": trj_id,
    #     "origin_time": query_time,
    #     "destination_time": ,
    #     "distance": distance in kilometers not meters contrary to OSRM returned distance,
    #     "rain_fall_rate": rainfall
    # }




                    
