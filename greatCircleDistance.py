# Great circle distance computes the shortest path distance of two projections on the surface of earth.

from math import radians, degrees, sin, cos, asin, acos, sqrt

def haversine(lat1, lat2, long1, long2):
    r = 6371 #km
    long1, lat1, long2, lat2 = map(radians, [long1, lat1, long2, lat2])
    dist_longtitude = long2-long1
    dist_latitude = lat2 - lat1

    a = sin(dist_latitude/2)**2 + cos(lat1)*cos(lat2)*sin(dist_longtitude/2)**2
    return 2*r*asin(sqrt(a))

print(haversine(37.72,41.8781, -89.2167,-86.6297))