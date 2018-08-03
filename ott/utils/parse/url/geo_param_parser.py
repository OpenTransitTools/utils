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
RADIUS_IDS = ['radius']
DISTANCE_IDS = ['distance']
PLACE = ['place', 'point', 'loc']

BBOX_MIN_LON_IDS = ['minLon', 'x1', 'e']
BBOX_MAX_LON_IDS = ['maxLon', 'x2', 'w']
BBOX_MIN_LAT_IDS = ['minLat', 'y1', 's']
BBOX_MAX_LAT_IDS = ['maxLat', 'y2', 'n']


class SimpleGeoParamParser(SimpleParamParser):

    def __init__(self, request, def_zoom=13, def_size=240):
        # import pdb; pdb.set_trace()
        super(SimpleGeoParamParser, self).__init__(request)
        self.lat = self.get_first_val_as_numeric(LAT_IDS)
        self.lon = self.get_first_val_as_numeric(LON_IDS)
        self.zoom = self.get_first_val_as_int(ZOOM_IDS, def_zoom)
        self.width = self.get_first_val_as_int(WIDTH_IDS, def_size)
        self.height = self.get_first_val_as_int(HEIGHT_IDS, def_size)

        self.radius = None
        self.top = None
        self.radius = None

        self.point = None
        self.bbox = None

    def has_coords(self):
        ret_val = False
        if self.lat and self.lon:
            ret_val = True
        return ret_val

    def has_radius(self):
        self._get_radius()
        ret_val = False
        if self.radius and self.has_coords():
            ret_val = True

        return ret_val

    def has_bbox(self):
        self._get_bbox()
        ret_val = self.bbox is not None
        return ret_val

    def get_bbox(self):

    def make_bbox(self):
        from ott.utils.geo.bbox import BBox
        return BBox(self.min_lat, self.max_lat, self.min_lon, self.max_lon)

    def to_point(self):
        point = geo_utils.make_point(self.lon, self.lat)
        return point

    def _get_radius(self):
        """ add more param queries here """
        self.radius = self.get_first_val_as_numeric(RADIUS_IDS)
        if not self.radius:
            distance = self.get_first_val_as_numeric(DISTANCE_IDS)
            if distance:
                self.radius = distance / 2

    def _get_bbox(self):
        if self.bbox is None:
            max_lat = self.get_first_val_as_numeric(BBOX_MAX_LAT_IDS)
            if max_lat:
                min_lat = self.get_first_val_as_numeric(BBOX_MIN_LAT_IDS)
                max_lon = self.get_first_val_as_numeric(BBOX_MAX_LON_IDS)
                min_lon = self.get_first_val_as_numeric(BBOX_MIN_LON_IDS)

                from ott.utils.geo.bbox import BBox
                self.bbox = BBox.make(min_lat, max_lat, min_lon, max_lon)


class GeoParamParser(ParamParser, SimpleGeoParamParser):

    # TODO: is params supposed to be 'request'
    def __init__(self, params, def_count=10, def_srid='4326'):
        super(GeoParamParser, self).__init__(params)
        self.limit = self.get_first_val(NUM_IDS, def_count)
        self.srid  = self.get_first_val(SRID_IDS, def_srid)
        self.name  = self.get_first_val(NAME_IDS)

    def to_point_srid(self, srid=None):
        if srid is None:
            srid = self.srid
        ret_val = geo_utils.make_point_srid(self.lon, self.lat, srid)
        return ret_val


class StopGeoParamParser(GeoParamParser, StopParamParser):
    pass