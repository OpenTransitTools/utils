import re
import math
import logging
log = logging.getLogger(__file__)

from ott.utils import object_utils
from ott.utils import html_utils

ZIP_CODE_RE = re.compile("[,\s]*\d{5}(?:[-\s]\d{4})?$")
ADDRESS_RE  = re.compile("^[0-9]+[\s\w]+\s(north|south|east|west|n|s|e|w){1,2}(?=\s|$)", re.IGNORECASE)


def parse_geojson_point(geojson):
    coord = geojson.get('coordinates')
    x = coord[0]
    y = coord[1]
    return x, y


def parse_geojson(geojson):
    ret_val = None
    try:
        if geojson.get('type') == 'Point':
            ret_val = parse_geojson_point(geojson)
    except Exception, e:
        log.info(e)
    return ret_val


def is_coord(str):
    ret_val = False
    try:
        ll = str.split(",")
        if float(ll[0].strip()) and float(ll[1].strip()):
            ret_val = True
    except:
        pass
    return ret_val


def is_address(str):
    """ does string look kinda-like an (US postal) address 
    """
    ret_val = False
    try:
        if ADDRESS_RE.search(str):
            ret_val = True
    except:
        pass
    return ret_val


def contains_coord(place):
    """ determine if the string has something that looks like a coord
    """
    ret_val = False
    coord = place
    if coord and "::" in coord:
        coord = place.split("::")[1]
    if is_coord(coord):
        ret_val = True
    return ret_val


def is_param_a_coord(request, type='place'):
    """ determine if the url has either a typeCoord url parameter, or a type::45.5,-122.5 param
    """
    ret_val = False
    coord = html_utils.get_first_param(request, type + 'Coord')
    if is_coord(coord):
        ret_val = True
    else:
        place = html_utils.get_first_param(request, type)
        if contains_coord(place):
            ret_val = True
    return ret_val


def get_coord_from_dict(coord, def_val=None):
    """ return lat,lon based on {"lat":y, "lon":x}
    """
    lat = object_utils.dval(coord, 'lat', def_val)
    lon = object_utils.dval(coord, 'lon', def_val)

    if lat == def_val:
        lat = object_utils.dval(coord, 'latitude', def_val)

    if lon == def_val:
        lon = object_utils.dval(coord, 'lng', def_val)
    if lon == def_val:
        lon = object_utils.dval(coord, 'longitude', def_val)
    return lat, lon


def to_OSPN(lon, lat):
    """ return Oregon State-Plane North X,Y for input lon,lat
    """
    lon = float(lon)
    lat = float(lat)
    x = ((6350713.93 -(111123.3583*(lat-45.1687259619)+9.77067* math.pow(lat-45.1687259619, 2) + 5.62487 * math.pow(lat-45.1687259619, 3) + 0.024544 * math.pow(lat-45.1687259619, 4) ))* math.sin(((3.14159265359*((120.5+lon) * math.sin(45.1687259*3.14159265359/180)))/180))+2500000)/0.3048
    y = ((111123.3583*(lat-45.1687259619)+9.77067* math.pow(lat-45.1687259619, 2)+5.62487*math.pow(lat-45.1687259619, 3)+0.024544*math.pow(lat-45.1687259619, 4))+(((6350713.93-(111123.3583*(lat-45.1687259619)+9.77067*math.pow(lat-45.1687259619, 2)+5.62487*math.pow(lat-45.1687259619, 3)+0.024544*math.pow(lat-45.1687259619,4)))*math.sin((3.14159265359*((120.5+lon)*math.sin(45.1687259*3.14159265359/180)))/180))*math.tan((3.14159265359*((120.5+lon)*math.sin(45.1687259*3.14159265359/180)))/360))+166910.7663)/0.3048
    x = round(x)
    y = round(y)
    return x,y


def to_lon_lat(x, y):
    """ return lon,lat from OSPN
    """
    x = float(x)
    y = float(y)
    lon = +((((math.atan(((x*0.3048)-2500000)/(6350713.93-((y*0.3048)-166910.7663))))*180)/(3.14159265359*0.709186016884))-120.5)
    lat = (45.1687259619+((((y*0.3048)-166910.7663)-(((x*0.3048)-2500000)*math.tan((math.atan(((x*0.3048)-2500000)/(6350713.93-((y*0.3048)-166910.7663))))/2)))*(0.000008999007999+(((y*0.3048)-166910.7663)-(((x*0.3048)-2500000)*math.tan((math.atan(((x*0.3048)-2500000)/(6350713.93-((y*0.3048)-166910.7663))))/2)))*(-7.1202E-015+(((y*0.3048)-166910.7663)-(((x*0.3048)-2500000)*math.tan((math.atan(((x*0.3048)-2500000)/(6350713.93-((y*0.3048)-166910.7663))))/2)))*(-3.6863E-020+(((y*0.3048)-166910.7663)-(((x*0.3048)-2500000)*math.tan((math.atan(((x*0.3048)-2500000)/(6350713.93-((y*0.3048)-166910.7663))))/2)))*-1.3188E-027)))))
    return lon,lat


def get_address_from_dict(address, def_val=None):
    """
        "street": "355 Binney St",
        "city": "Cambridge",
        "region_name": "Massachusetts",
        "postal_code": "02139",
        "country_code": "US"
    """
    street = object_utils.dval(address, 'street', def_val)
    city   = object_utils.dval(address, 'city',   def_val)
    state  = object_utils.dval(address, 'state',  def_val)
    zip    = object_utils.dval(address, 'zip',    def_val)

    if street == def_val:
        street = object_utils.dval(address, 'address', def_val)
    if state == def_val:
        state = object_utils.dval(address, 'region_name', def_val)
    if zip == def_val:
        zip = object_utils.dval(address, 'postal_code', def_val)

    return street, city, state, zip


def get_coord_from_request(request, param_name='placeCoord', def_val=None):
    """ return lat,lon based on either a coord name, or lat/lon parametres
    """
    # import pdb; pdb.set_trace()
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
    """ return a fully built out NAME::lat,lon string based on params in the request
    """
    ret_val = def_val
    try:
        # step 1: get name (which may/may not be a fully NAME::COORD string...
        name = html_utils.get_first_param(request, param_name, def_val)
        if name:
            ret_val = name
        else:
            name = def_val

        # step 2: find a nameCoord or lat,lon in the request...
        if not contains_coord(name):
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
    """ PDX::-122,45::Portland ... will return the Portland portion, if it exists...
    """
    ret_val = def_val
    if place and "::" in place:
        p = place.split("::")
        if len(p) >= 3:
            ret_val = p[2]
    return ret_val


def ll_from_str(place, def_val=None, to_float=False):
    """ break 45.5,-122.5 to lat,lon components
    """
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


def get_name_city_from_string(str):
    """ will break up something like 834 SE X Street, Portland <97xxx> into '834 SE X Street' and 'Portland'
    """
    name = None
    city = None
    try:
        v = str.split(',')
        name = v[0].strip()
        city = v[1].strip()
        city = ZIP_CODE_RE.sub('', city)
    except:
        pass
    finally:
        if name == None:
            name = str
            city = None
    return name,city


def is_nearby(latA, lonA, latB, lonB, decimal_diff=0.0015):
    """ compares lat/lon A vs lat/lon B to sees whether their values
        are within a certain decimal place of each other
        NOTE: default is 0.0015 ... if the distant between latA and latB, and lonA and lonB is
              each 0.0015 absolute differnce  
    """
    ret_val = False
    try:
        lat_diff = abs(latA - latB)
        lon_diff = abs(lonA - lonB)
        if lat_diff < decimal_diff and lon_diff < decimal_diff:
            ret_val = True
    except:
        pass
    return ret_val


def make_place(name, lat, lon, city=None, place=None):
    ret_val = {'name':name, 'city':city, 'lat':lat, 'lon':lon, 'place':place}
    return ret_val


def from_place_str(place):
    """ will return a dict of descrete values from a place string...
        ala PDX::45.5,-122.5::Portland will populate this dict...
    """
    ret_val = None
    try:
        name = name_from_named_place(place, place)
        lat,lon =  ll_from_str(place, to_float=True)
        city = city_from_named_place(place)
        ret_val = make_place(name, lat, lon, city, place)
    except:
        pass
    return ret_val


if __name__ == "__main__":
    print to_OSPN(-122.5, 45.5)
