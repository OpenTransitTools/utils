from . import object_utils
from . import html_utils

import re
import math
import logging
log = logging.getLogger(__file__)


ZIP_CODE_RE = re.compile("[,\s]*\d{5}(?:[-\s]\d{4})?$")
ADDRESS_RE  = re.compile("^[0-9]+[\s\w]+\s(north|south|east|west|n|s|e|w){1,2}(?=\s|$)", re.IGNORECASE)


def BBox(t, b, l, r):
    """
    TODO: make a more flexable class
    """
    return "[{}, {}, {}, {}]".format(t, b, l, r)


def bbox(min_lat, max_lat, min_lon, max_lon):
    """
    minLat=45.50854243338104&maxLat=45.519789433696744&minLon=-122.6960849761963&maxLon=-122.65591621398927):
    """
    return BBox(max_lat, min_lat, max_lon, min_lon)


def make_geojson_bbox(min_lat, max_lat, min_lon, max_lon, srid=None):
    """
    see: https://gis.stackexchange.com/questions/25797/select-bounding-box-using-postgis
    note: 5-pt POLYGON ulx uly, urx ury, lrx lry, llx llr, ulx uly
    """
    polygon = 'POLYGON(({2} {1}, {3} {1}, {3} {0}, {2} {0}, {2} {1}))'.format(min_lat, max_lat, min_lon, max_lon)
    if srid:
        polygon = 'SRID={0};{1}'.format(srid, polygon)
    return polygon


def make_geojson_point(x, y, srid=None):
    point = 'POINT({0} {1})'.format(x, y)
    if srid:
        point = 'SRID={0};{1}'.format(srid, point)
    return point


# TODO - rename these older make_point methods?
def make_point(lon, lat, srid=None):
    return make_geojson_point(lon, lat, srid)

def make_point_srid(lon, lat, srid='4326'):
    return make_geojson_point(lon, lat, srid)


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
    except Exception as e:
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
    return x, y


def to_meters(lon, lat):
    """
    convert from long/lat to google mercator (or EPSG:4326 to EPSG:900913 or EPSG:3857 Web Mercator)
    :see: https://gist.github.com/springmeyer/871897
    """
    lon = float(lon)
    lat = float(lat)

    x = lon * 20037508.34 / 180.0
    t = math.tan((90.0 + lat) * math.pi / 360.0)
    y = math.log(t) / (math.pi / 180.0)
    y = y * 20037508.34 / 180.0

    return x, y


def to_lon_lat(x, y):
    """ return lon,lat from OSPN
    """
    x = float(x)
    y = float(y)
    lon = +((((math.atan(((x*0.3048)-2500000)/(6350713.93-((y*0.3048)-166910.7663))))*180)/(3.14159265359*0.709186016884))-120.5)
    lat = (45.1687259619+((((y*0.3048)-166910.7663)-(((x*0.3048)-2500000)*math.tan((math.atan(((x*0.3048)-2500000)/(6350713.93-((y*0.3048)-166910.7663))))/2)))*(0.000008999007999+(((y*0.3048)-166910.7663)-(((x*0.3048)-2500000)*math.tan((math.atan(((x*0.3048)-2500000)/(6350713.93-((y*0.3048)-166910.7663))))/2)))*(-7.1202E-015+(((y*0.3048)-166910.7663)-(((x*0.3048)-2500000)*math.tan((math.atan(((x*0.3048)-2500000)/(6350713.93-((y*0.3048)-166910.7663))))/2)))*(-3.6863E-020+(((y*0.3048)-166910.7663)-(((x*0.3048)-2500000)*math.tan((math.atan(((x*0.3048)-2500000)/(6350713.93-((y*0.3048)-166910.7663))))/2)))*-1.3188E-027)))))
    return lon, lat


def calculate_bounds(x, y, zoom, width, height):
    """
    with X (lon), Y (lat), zoom, width & height, calculate and return a bbox for a call to WMS
    :return: bbox for a call to GeffoServer WMS
    """
    resolutions = [256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5, 0.25, 0.125, 0.0625, 0.03125]

    # get zoom to match a resolution
    if zoom < 0: zoom = 0
    if zoom > len(resolutions): zoom = len(resolutions)
    zoom -= 1

    # get the actual resolution
    res = resolutions[zoom]

    w_deg = width * res
    h_deg = height * res

    extent = BBox(
              x - w_deg / 2,
              y + h_deg / 2,
              x + w_deg / 2,
              y - h_deg / 2
    )
    return extent


def read_shp(shp_dir_path):
    """
    read an ESRI .shp file
    :param shp_dir_path is the directory where the .shp and .dbf file live:
    :return: shapefile.Reader
    """
    import shapefile
    shp = open(shp_dir_path + ".shp", "rb")
    dbf = open(shp_dir_path + ".dbf", "rb")
    r = shapefile.Reader(shp=shp, dbf=dbf)
    return r


def read_shp_zip(shp_zip_file):
    """
    read an ESRI .shp file that's packaged in a .zip file
    :return: shapefile.Reader
    """
    r = read_shp(shp_dir)
    return r


def read_shp_zip_url(shp_zip_url):
    """
    download a .zip file from a url, which we assume is an ESRI .shp file
    :return: shapefile.Reader
    """
    r = read_shp_zip(shp_zip_file)
    return r


def to_lon_lat_tuple(t):
    return to_lon_lat(t[0], t[1])


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


def xy_to_url_param_str(x, y, x_name="lon", y_name="lat", sep="&", check_lat_lon=True):
    if check_lat_lon:
        x = float(x)
        y = float(y)
        if y > 90.0 or y < -90.0:
            t = x
            x = y
            y = t

    ret_val = "{}={}{}{}={}".format(x_name, x, sep, y_name, y)
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


def distance(latA, lonA, latB, lonB, R=6371e3):
    """
    gives d in metres
    :see https://www.movable-type.co.uk/scripts/latlong.html:
    """
    #import pdb; pdb.set_trace()
    y1 = math.radians(float(latA))
    y2 = math.radians(float(latB))
    deltaX = math.radians(float(float(lonB) - float(lonA)))
    d = math.acos(math.sin(y1)*math.sin(y2) + math.cos(y1)*math.cos(y2) * math.cos(deltaX) ) * R
    ret_val = round(d, 2)
    return ret_val
# todo duplicate to above --
# todo dist = num_utils.distance_mi(s.stop_lat, s.stop_lon, geo_params.lat, geo_params.lon)


def list_sort(obj_list, sort_on_attrib='distance', reverse_order=False, assign_order=False):
    """
    sort a python list [] by attribute, and assign order
    """

    # step 1: sort the list
    obj_list.sort(key=lambda x: object_utils.safe_get(sort_on_attrib), reverse=reverse_order)

    # step 2: assign order
    if assign_order:
        for i, s in enumerate(obj_list):
            s.order = i + 1

    return obj_list


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


def sv_url(lat, lon, zoom=17, protocol="//"):
    """
    :return: static url to street view from maps.google.com
    """

    tmpl = "{protocol}maps.google.com/maps?output=svembed&layer=c&cbp=13,,,,&cbll={lat},{lon}&ll={lat},{lon}&z={zoom}"
    ret_val = tmpl.format(lat=lat, lon=lon, zoom=zoom, protocol=protocol)
    return ret_val


def sv_iframe(lat, lon, zoom=17, protocol="//"):
    """
    :return iframe to street view from maps.google.com
    """
    tmpl = "<iframe width='100%' height='100%' frameborder='0' scrolling='no' marginheight='0' marginwidth='0' src='{url}'></iframe>"
    url = sv_url(lat, lon, zoom, protocol)
    ret_val = tmpl.format(url=url)
    return ret_val


if __name__ == "__main__":
    print(to_OSPN(-122.5, 45.5))
