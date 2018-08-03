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

        self._radius = None
        self._bbox = None
        self._point = None

    @property
    def radius(self):
        return self._get_radius()

    @property
    def point(self):
        return self._get_point()

    @property
    def bbox(self):
        return self._make_bbox()

    def has_coords(self):
        ret_val = False
        if self.lat and self.lon:
            ret_val = True
        return ret_val

    def has_radius(self):
        ret_val = False
        if self.radius and self.has_coords():
            ret_val = True
        return ret_val

    def has_bbox(self):
        ret_val = self.bbox is not None
        return ret_val

    def to_point(self):
        point = geo_utils.make_point(self.lon, self.lat)
        return point

    def _get_radius(self):
        """ add more param queries here """
        if not self._radius:
            self._radius = self.get_first_val_as_numeric(RADIUS_IDS)
            if not self._radius:
                distance = self.get_first_val_as_numeric(DISTANCE_IDS)
                if distance:
                    self._radius = distance / 2
        return self._radius

    def _get_point(self):
        if self._point is None:
            from ott.utils.geo.point import Point
            self._point = Point(self.lon, self.lat, self.radius)
        return self._point

    def _make_bbox(self):
        if self._bbox is None:
            max_lat = self.get_first_val_as_numeric(BBOX_MAX_LAT_IDS)
            if max_lat:
                min_lat = self.get_first_val_as_numeric(BBOX_MIN_LAT_IDS)
                max_lon = self.get_first_val_as_numeric(BBOX_MAX_LON_IDS)
                min_lon = self.get_first_val_as_numeric(BBOX_MIN_LON_IDS)

            from ott.utils.geo.bbox import BBox
            self._bbox = BBox(min_lat, max_lat, min_lon, max_lon)
        return self._bbox


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