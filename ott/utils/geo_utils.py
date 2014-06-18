import logging
log = logging.getLogger(__file__)

def has_coord(place):
    ''' determine if the string has something that looks like a coord
    '''
    ret_val = False
    coord = place
    if coord and "::" in coord:
        coord = place.split("::")[1]
    if coord and "," in coord:
        ret_val = True
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

