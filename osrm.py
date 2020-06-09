import requests
import json
import glob
from geojson import MultiPoint, Feature, FeatureCollection, dump
from os import path

crs = {
"type":"trajectory",
"properties":{
    "name": "EPSG:4326"
}
}
parent_dir = "geopoints"

for geofile in glob.glob(path.join(parent_dir, "*.geojson")):
    geo_string = []

    trj_id = path.splitext(path.basename(geofile))[0]
    with open(geofile, "r") as file:
        content = file.read()

    geometry = json.loads(content)
    geometry = geometry['features'][0]['geometry']['coordinates']

    for geo in geometry:
        geo_ = ','.join([str(elem) for elem in geo])
        geo_string.append(geo_)
    
    list_geometry = ';'.join([str(elem) for elem in geo_string])
    url = 'http://ivolab:5000/match/v1/driving/' + list_geometry + '?steps=false&geometries=geojson&overview=full&annotations=false'

    response = requests.get(url)
    mapmatched_geopoints = response.json()['matchings'][0]['geometry']

    prop = {
        "country": "Singapore"
    }
    geometryJSON = Feature(geometry = mapmatched_geopoints, properties = prop)
    geometryJSON = FeatureCollection([geometryJSON], crs = crs)

    with open("mapmatched/{}.geojson".format(trj_id), "w") as file:
        dump(geometryJSON, file)
    print("Trajectory {}'s geojson has been generated".format(trj_id))
