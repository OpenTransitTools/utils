from ott.utils import geo_utils
from ott.utils import num_utils


class BBox(object):

    srid = '4326'

    def __init__(self, min_lat, max_lat, min_lon, max_lon):
        self.min_lat = num_utils.to_float(min_lat)
        self.max_lat = num_utils.to_float(max_lat)
        self.min_lon = num_utils.to_float(min_lon)
        self.max_lon = num_utils.to_float(max_lon)

    def to_geojson(self):
        return geo_utils.make_geojson_bbox(self.min_lat, self.max_lat, self.min_lon, self.max_lon, self.srid)

    def to_gtfsdb_bbox(self):
        from gtfsdb.util import BBox
        bbox = BBox(min_lat=self.min_lat, max_lat=self.max_lat, min_lon=self.min_lon, max_lon=self.max_lon, srid=self.srid)
        return bbox

    def is_valid(self):
        return self.min_lat and self.max_lat and self.min_lon and self.max_lon
