import requests
import json
import glob
from os import path
import numpy as np
import time

def map_image_generator(sub_key, trj_id, latitude_origin, longitude_origin, latitude_dest, longitude_dest):
    '''
        Parameters: 
            sub_key : subscription key example => DHFtDtL2CTnX1RKS2bHCPSYJsNm3PfBmmEAMpSFKRwQ
            trj_id : integer value usage: name of the map image example 100
            latitude_origin, longitude_origin, latitude_dest, longitude_dest : float values for 
            latitude and longitude for origin and destination respectively.

        return
            map image trj_id.png as the image extension example 100.png
            routeLengthInMeters float example 12342.5
    '''
    formated_coords = []
    origin_dest = latitude_origin+','+longitude_origin+':'+latitude_dest+','+longitude_dest

    response_data = requests.get('https://atlas.microsoft.com/route/directions/json?subscription-key='+sub_key+'&RouteType=fastest&traffic=true&api-version=1.0&query='+origin_dest)
    routeLengthInMeters = response_data.json()['routes'][0]['summary']['lengthInMeters']

    coordinates = response_data.json()['routes'][0]['legs'][0]['points']
    for cord_pair in coordinates:
        formated_coords.append([cord_pair['longitude'],cord_pair['latitude']])

    data = {
    'type': 'FeatureCollection',
    'features': [
        {
        'type': 'Feature',
        'geometry': {
            'type': 'LineString',
            'coordinates': formated_coords
        },
        'properties': {
            'country': 'Singapore',
            'start': '2019-04-20T04:31:17.000000000',
            'end': '2019-04-20T04:52:28.000000000'
        }
        }
    ]
    }

    max_lng = np.array(data['features'][0]['geometry']['coordinates'])[:,0].max()
    min_lng = np.array(data['features'][0]['geometry']['coordinates'])[:,0].min()
    max_lat = np.array(data['features'][0]['geometry']['coordinates'])[:,1].max()
    min_lat = np.array(data['features'][0]['geometry']['coordinates'])[:,1].min()
    lat = min_lat + (max_lat - min_lat)/2
    lng = min_lng + (max_lng - min_lng)/2

    response = requests.post('https://atlas.microsoft.com/mapData/upload?subscription-key='+sub_key+'&api-version=1.0&dataFormat=geojson', json=data)

    if not response.status_code == requests.codes.ok:
        if 'Location' in response.headers:
            Location = response.headers['Location']
            resp_url = 'https://atlas.microsoft.com/mapData/operations/'
            length = len(resp_url) 
            status_uri = Location[length:-16]

            # Making a GET request 
            print(resp_url+status_uri)
            response_2 = requests.get(resp_url+status_uri+'?api-version=1.0&subscription-key='+sub_key) 
            if 'status' in response_2.json():
                while response_2.json()['status'] == 'Running':
                    response_2 = requests.get(resp_url+status_uri+'?api-version=1.0&subscription-key='+sub_key) 
                    print('Waiting...')
            print(response_2.json())
            # check status code for response received 
            # success code - 200 
            
            if not response_2.status_code == requests.codes.ok:
                lc = response_2.headers['location'] if response_2.headers['location'] else response_2.headers['Location']
                ln = len('https://atlas.microsoft.com/mapData/metadata/')
                
                udId = lc[ln:-16]

                style = 'layer=basic&style=dark&zoom=11&center='+str(lng)+'%2C'+str(lat)+'&path=lcf78731|fc0000FF|lw4|la1.0|fa1.0||'
                map_response = requests.get('https://atlas.microsoft.com/map/static/png?subscription-key='+sub_key+'&api-version=1.0&'+style+'udid-'+udId)
                print(map_response)
                with open('output/'+str(trj_id)+'.png','wb') as f:
                    f.write(map_response.content)

                req = requests.delete('https://atlas.microsoft.com/mapData/'+udId+'?api-version=1.0&subscription-key='+sub_key)
                print(req)
                return str(trj_id)+'.png', routeLengthInMeters

            else:
                print(response_2.json())
                print("Something went wrong, get request for udId failed!!")
        else:
            print("Bad response")
    else:
        print("Something went wrong during data upload!!")
    return 'failed', routeLengthInMeters

# import glob
# Example on how to call the function 
parent_dir = 'test'
paths = glob.glob(path.join(parent_dir, "*.geojson"))
for geofile in paths:
    
    # counter += 1
    geo_string = []
    trj_id = path.splitext(path.basename(geofile))[0]
    if not path.exists('output/'+str(trj_id)+'.png'):
        with open(geofile, "r") as file:
            content = file.read()
        
        data = json.loads(content)
        origin = data['features'][0]['geometry']['coordinates'][0]
        dest = data['features'][0]['geometry']['coordinates'][-1]
        print(origin, dest)
        map_image_name, distance = map_image_generator('DHFtDtL2CTnX1RKS2bHCPSYJsNm3PfBmmEAMpSFKRwQ', trj_id=trj_id, 
        latitude_origin=str(origin[1]), longitude_origin=str(origin[0]), latitude_dest=str(dest[1]), longitude_dest=str(dest[0]))
        print(map_image_name, distance)


# import requests
# import json
# import glob
# # from geojson import MultiPoint, Feature, FeatureCollection, dump
# from os import path
# import numpy as np
# import time

# # API_KEY = 'DHFtDtL2CTnX1RKS2bHCPSYJsNm3PfBmmEAMpSFKRwQ'
# # API_KEY = '53EIeobb-HDLQ5KJrW5P6KeeDoKXZFAUlArGW4bwzZc'
# # API_KEY = 'bScOhbRfaX2mbSA1sBR8eRiGBKKgl1NdSyakQSi-aXs'
# API_KEY = 'f4xPafAV9z3SawPl7YzG5qdyUr-P9Oozy6KoyaMQpjs'
# parent_dir = 'geo_files'
# data = ''
# # counter = 0
# # dt_points = []
# # mean_points = np.array([0])
# # paths = glob.glob(path.join(parent_dir, "*.geojson"))

# points = []
# origin_dest = '1.370959,103.872222:1.373563,103.772978'
# dt = requests.get('https://atlas.microsoft.com/route/directions/json?subscription-key='+API_KEY+'&api-version=1.0&query='+origin_dest)

# dts = dt.json()['routes'][0]['legs'][0]['points']
# for dt in dts:
#     points.append([dt['longitude'],dt['latitude']])
# # points.append([point['longitude'],point['latitude']] for point in dts)
# # print(points[:10])
# # print(dt['routes'][0]['legs'][0]['points'][:100])

# data = {
#   'type': 'FeatureCollection', 
#   'crs': 
#    {
#       'type': 'trajectory', 
#       'properties': 
#       {
#           'name': 'EPSG:4326'
#           }
#    }, 
#   'features': [
#     {
#       'type': 'Feature',
#       'geometry': {
#         'type': 'LineString',
#         'coordinates': points
#       },
#       'properties': {
#         'country': 'Singapore',
#         'start': '2019-04-20T04:31:17.000000000',
#         'end': '2019-04-20T04:52:28.000000000'
#       }
#     }
#   ]
# }

# print(json.dumps(data))
# # print(json.dumps(data))
# # for geofile in paths:
# #     counter += 1
# #     if counter < 223:
# #         continue
# #     geo_string = []

# #     trj_id = path.splitext(path.basename(geofile))[0]
# #     with open(geofile, "r") as file:
# #         content = file.read()
    
# #     data = json.loads(content)
# # data = json.dumps(obj)

#     # number_data_points = len(data['features'][0]['geometry']['coordinates'])
# max_lng = np.array(data['features'][0]['geometry']['coordinates'])[:,0].max()
# min_lng = np.array(data['features'][0]['geometry']['coordinates'])[:,0].min()
# max_lat = np.array(data['features'][0]['geometry']['coordinates'])[:,1].max()
# min_lat = np.array(data['features'][0]['geometry']['coordinates'])[:,1].min()
# lat = min_lat + (max_lat - min_lat)/2
# lng = min_lng + (max_lng - min_lng)/2
# # print(max_lng,max_lat)
# # print(lng,lat)
# # print(trj_id, number_data_points)
# # center_point = number_data_points//2
# # lat = data['features'][0]['geometry']['coordinates'][center_point][0]
# # lng = data['features'][0]['geometry']['coordinates'][center_point][1]

# response = requests.post('https://atlas.microsoft.com/mapData/upload?subscription-key='+API_KEY+'&api-version=1.0&dataFormat=geojson', json=json.dumps(data), timeout=200.0)
# # response = requests.post('https://atlas.microsoft.com/mapData/upload?subscription-key='+API_KEY+'&api-version=1.0&dataFormat=geojson', json=data)

# if not response.status_code == requests.codes.ok:
#     Location = response.headers['Location']
#     resp_url = 'https://atlas.microsoft.com/mapData/operations/'

#     # print("Length : ",Location)
#     length = len(resp_url) 
#     status_uri = Location[length:-16]
#     # print(resp_url+status_uri)
#     # Making a GET request 
#     print(resp_url+status_uri)
#     r = requests.get(resp_url+status_uri+'?api-version=1.0&subscription-key='+API_KEY, timeout=30.0) 

#     # check status code for response received 
#     # success code - 200 
#     print(r.json())
#     if 'status' in r.json():
#         while r.json()['status'] == 'Running':
#             r = requests.get(resp_url+status_uri+'?api-version=1.0&subscription-key='+API_KEY) 
#             print('Waiting...')
#             print(r.json())
#     lc = r.headers['location'] if r.headers['location'] else r.headers['Location']
#     ln = len('https://atlas.microsoft.com/mapData/metadata/')
#     udId = lc[ln:-16]
#     zooms = ['17','16','15','14','13','12','11']
#     # x = number_data_points//140
#     # if x > 5:
#     #     x = 5
#     x = 6
#     style = 'layer=basic&style=dark&zoom='+zooms[x]+'&center='+str(lng)+'%2C'+str(lat)+'&path=lcf78731|fc0000FF|lw4|la1.0|fa1.0||'
#     map_response = requests.get('https://atlas.microsoft.com/map/static/png?subscription-key='+API_KEY+'&api-version=1.0&'+style+'udid-'+udId, timeout=30.0)
#     # print content of request 
#     # print(map_response.content) 

#     with open(str(1000)+'.png','wb') as f:
#         f.write(map_response.content)

#     req = requests.delete('https://atlas.microsoft.com/mapData/'+udId+'?api-version=1.0&subscription-key='+API_KEY, timeout=30.0)
#     print(req)
# else:
#     print("Something went wrong during data upload!!")