from ott.utils import object_utils

import math
import logging
log = logging.getLogger(__file__)


def distance_km(lat1, lon1, lat2, lon2):
    """ return distance between two points in km using haversine
        http://en.wikipedia.org/wiki/Haversine_formula
        http://www.platoscave.net/blog/2009/oct/5/calculate-distance-latitude-longitude-python/
        Author: Wayne Dyck
    """
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
    """ return distance between two points in miles
    """
    km = distance_km(lat1, lon1, lat2, lon2)
    return km * 0.621371192


def to_int(val, def_val):
    ret_val = def_val
    try:
        ret_val = int(val)
    except:
        pass
    return ret_val


def to_float(val, def_val=None):
    ret_val = def_val
    try:
        ret_val = float(val)
    except:
        pass
    return ret_val


def array_item_to_int(list, index, def_val=None):
    ret_val = def_val
    try:
        ret_val = int(object_utils.safe_array_val(list, index))
    except:
        pass
    return ret_val


def meters_to_feet(meters):
    return meters * 0.30480


def feet_to_meters(feet, inches=0):
    tot_inches = feet * 12 + inches
    meters = tot_inches * 0.0254
    return meters


def feet_to_inches(feet, do_round=False):
    inches = feet * 12
    if do_round:
        inches = round(inches)
    return inches


def inches_to_feet_inches(inches, include_units=True):
    inches = round(inches)
    feet = int(math.floor(inches / 12))
    inches = int(inches % 12)
    ret_val = {'feet': feet, 'inches': inches}

    if include_units:
        ret_val['funits'] = 'foot' if feet == 1 or feet == -1 else 'feet'
        ret_val['iunits'] = 'inch' if inches == 1 or inches == -1 else 'inches'

    return ret_val


def feet_to_feet_inches(feet, include_units=True):
    inches = feet * 12
    return inches_to_feet_inches(inches, include_units)


def degrees_to_meters(degrees):
    """
    111195 = (Earth mean radius)*PI/180
    (supposedly 'maximum error using this method is ~ 0.1%')
    :see: https://stackoverflow.com/questions/12204834/get-distance-in-meters-instead-of-degrees-in-spatialite
    """
    ret_val = 111195 * degrees
    return ret_val


def degrees_to_feet(degrees):
    meters = degrees_to_meters(degrees)
    feet = meters_to_feet(meters)
    ret_val = int(math.floor(feet))
    return ret_val


def degrees_to_feet_inches(degrees):
    meters = degrees_to_meters(degrees)
    feet = meters_to_feet(meters)
    ret_val = feet_to_feet_inches(feet)
    return ret_val

