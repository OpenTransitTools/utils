import logging
log = logging.getLogger(__file__)

import html_utils

def is_coord(str):
    ret_val = False
    try:
        ll = str.split(",")
        if float(ll[0].strip()) and float(ll[1].strip()):
            ret_val = True
    except:
        pass
    return ret_val

def has_coord(place):
    ''' determine if the string has something that looks like a coord
    '''
    ret_val = False
    coord = place
    if coord and "::" in coord:
        coord = place.split("::")[1]
    if is_coord(coord):
        ret_val = True
    return ret_val


def get_coord_from_request(request, param_name='placeCoord', def_val=None):
    ''' return lat,lon based on either a coord name, or lat/lon parametres
    '''
    ret_val = def_val
    try:
        c = html_utils.get_first_param(request, param_name)
        if c and ',' in c:
            ret_val = c.strip()
        else:
            lat = html_utils.get_first_param(request, 'lat')
            lon = html_utils.get_first_param(request, 'lon')
            if lat and lon:
                ret_val = "{0},{1}".format(lat.strip(), lon.strip())
    except:
        pass 
    return ret_val


def get_named_param_from_request(request, param_name, def_val=None):
    ''' return a fully built out NAME::lat,lon string based on params in the request
    '''
    ret_val = def_val
    try:
        # step 1: get name (which may/may not be a fully NAME::COORD string...
        name = html_utils.get_first_param(request, param_name, def_val)
        if name:
            ret_val = name
        else:
            name = def_val

        # step 2: find a nameCoord or lat,lon in the request...
        if not has_coord(name):
            coord = get_coord_from_request(request, param_name + 'Coord')

            # step 3: if we have a coord, then make the return with that info
            if name and coord:
                ret_val = "{0}::{1}".format(name.strip(), coord)
            elif coord:
                ret_val = coord
    except:
        pass 
    return ret_val

def solr_to_named_param(doc, def_val=None):
    ret_val = def_val
    try:
        name = html_utils.html_escape(doc['name'])
        lat  = doc['lat']
        lon  = doc['lon']
        ret_val = "{0}::{1},{2}".format(name, lat, lon)
    except:
        pass
    return ret_val

def solr_to_named_plus_city(doc, def_val):
    ret_val = def_val
    try:
        ret_val = solr_to_named_param(doc, def_val)
        city = html_utils.html_escape(doc['city'])
        if city:
            ret_val = "{0}::{1}".format(ret_val, city)
    except:
        pass
    return ret_val


def name_from_named_place(place, def_val=None):
    ret_val = def_val
    if place and "::" in place:
        ret_val = place.split("::")[0]
    return ret_val

def city_from_named_place(place, def_val=None):
    ''' PDX::-122,45::Portland ... will return the Portland portion, if it exists...
    '''
    ret_val = def_val
    if place and "::" in place:
        p = place.split("::")
        if len(p) >= 3:
            ret_val = p[2]
    return ret_val

def ll_from_str(place, def_val=None, to_float=False):
    ''' break 45.5,-122.5 to lat,lon components
    '''
    lat = def_val
    lon = def_val
    try:
        coord = place
        if "::" in place:
            coord = place.split("::")[1]
        ll  = coord.split(',')
        la  = ll[0].strip()
        lo  = ll[1].strip()
        laf = float(la)
        lof = float(lo)
        if to_float:
            lat = laf
            lon = lof
        else:
            lat = la
            lon = lo
    except:
        pass
    return lat,lon


def from_place_str(place):
    ''' will return a dict of descrete values from a place string...
        ala PDX::45.5,-122.5::Portland will populate this dict...
    '''
    ret_val = {'name':None, 'city':None, 'lat':None, 'lon':None, 'place':place}
    try:
        ret_val['name'] = name_from_named_place(place, place)
        lat,lon =  ll_from_str(place, to_float=True)
        ret_val['lat'] = lat
        ret_val['lon'] = lon
        ret_val['city'] = city_from_named_place(place)
    except:
        pass
    return ret_val

