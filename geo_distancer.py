# https://www.geeksforgeeks.org/program-distance-two-points-earth/

# Python 3 program to calculate Distance Between Two Points on Earth
from math import radians, cos, sin, asin, sqrt

from numpy import float128


def distance(lat1, lat2, lon1, lon2):
    '''Returns the distance between 2 geocoordinates in KM'''
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2

    c = 2 * asin(sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371
    
    # calculate the result
    return(c * r)

def calculate_points_radius(lat0:float,lng0:float,radiuskm:float):
    # radians which converts from degrees to radians.
    # lat0 = radians(lat0)
    # lng0 = radians(lng0)
    C = 40075
    R_1DEG_LAT = C / 360.0
    def R_1DEG_LON(lat_deg:float):
        lat = radians(lat_deg)
        return (cos(lat) * C) / 360.0
    r_lat = radiuskm / R_1DEG_LAT
    r_lon = radiuskm / R_1DEG_LON(lat0)
    
    def deg_mod_lat(degs:float):
        return ((degs + 90.0) % 180) - 90.0
    def deg_mod_lon(degs:float):
        return ((degs + 180.0) % 360) - 180.0
        
    
    north = (deg_mod_lat(lat0 + r_lat), lng0)
    east = (lat0, deg_mod_lon(lng0 + r_lon))
    south = (deg_mod_lat(lat0 - r_lat), lng0)
    west = (lat0, deg_mod_lon(lng0 - r_lon))
    # https://stackoverflow.com/questions/4000886/gps-coordinates-1km-square-around-a-point
    
    return (north, east, south, west)
    

# driver code
lat1 = 53.32055555555556
lat2 = 53.31861111111111
lon1 = -1.7297222222222221
lon2 = -1.6997222222222223
print(distance(lat1, lat2, lon1, lon2), "K.M")

(north, east, south, west) = calculate_points_radius(lat1, lon1, 1.5)
print(distance(lat1, north[0], lon1, north[1]), "K.M")
print(distance(lat1, east[0], lon1, east[1]), "K.M")


