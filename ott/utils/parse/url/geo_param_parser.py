from .param_parser import ParamParser, SimpleParamParser
from .stop_param_parser import StopParamParser
from ott.utils import geo_utils


NAME_IDS = ['name', 'desc']
NUM_IDS = ['num',  'count', 'limit']
LON_IDS = ['x', 'lon']
LAT_IDS = ['y', 'lat']
ZOOM_IDS = ['z', 'zoom']
WIDTH_IDS = ['w', 'width']
HEIGHT_IDS = ['h', 'height']
SRID_IDS = ['srid']
PLACE = ['place', 'point', 'loc']


class SimpleGeoParamParser(SimpleParamParser):

    def __init__(self, request, def_zoom=13, def_size=240):
        # import pdb; pdb.set_trace()
        super(SimpleGeoParamParser, self).__init__(request)
        self.lat   = self.get_first_val_as_numeric(LAT_IDS)
        self.lon = self.get_first_val_as_numeric(LON_IDS)
        self.zoom = self.get_first_val_as_int(ZOOM_IDS, def_zoom)
        self.width = self.get_first_val_as_int(WIDTH_IDS, def_size)
        self.height = self.get_first_val_as_int(HEIGHT_IDS, def_size)

    def has_coords(self):
        ret_val = False
        if self.lat and self.lon:
            ret_val = True
        return ret_val

    def to_point(self):
        point = geo_utils.make_point(self.lon, self.lat)
        return point


class GeoParamParser(ParamParser, SimpleGeoParamParser):

    # TODO: is params supposed to be 'request'
    def __init__(self, params, def_count=10, def_srid='4326'):
        super(GeoParamParser, self).__init__(params)
        self.limit = self.get_first_val(NUM_IDS, def_count)
        self.srid  = self.get_first_val(SRID_IDS, def_srid)
        self.name  = self.get_first_val(NAME_IDS)
        # TODO: parse place variable into name/lat/lon/etc...

    def to_point_srid(self, srid=None):
        if srid is None:
            srid = self.srid
        ret_val = geo_utils.make_point_srid(self.lon, self.lat, srid)
        return ret_val


class StopGeoParamParser(GeoParamParser, StopParamParser):
    pass