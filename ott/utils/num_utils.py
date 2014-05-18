import math
import logging
log = logging.getLogger(__file__)

def distance_km(lat1, lon1, lat2, lon2):
    ''' return distance between two points in km using haversine
        http://en.wikipedia.org/wiki/Haversine_formula
        http://www.platoscave.net/blog/2009/oct/5/calculate-distance-latitude-longitude-python/
        Author: Wayne Dyck
    '''
    ret_val = 0
    radius = 6371 # km
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)

    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    ret_val = radius * c

    return ret_val


def distance_mi(lat1, lon1, lat2, lon2):
    ''' return distance between two points in miles
    '''
    km = distance_km(lat1, lon1, lat2, lon2)
    return km * 0.621371192


def to_int(val, def_val):
    ret_val = def_val
    try:
        ret_val = int(val)
    except:
        pass
    return ret_val

