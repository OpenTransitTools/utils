from ott.utils import geo_utils
from ott.utils import num_utils


class Point(object):

    srid = '4326'

    def __init__(self, x, y, radius=None):
        self.x = num_utils.to_float(x)
        self.y = num_utils.to_float(y)
        self.radius = num_utils.to_float(radius) # distance from the point

    @property
    def lat(self): return self.y

    @property
    def lon(self): return self.x

    def to_geojson(self):
        return geo_utils.make_geojson_point(self.x, self.y, self.srid)

    def is_valid(self):
        return self.x and self.y

    def has_radius(self):
        return isinstance(self.radius, float)

    def to_geojson_point(self):
        return geo_utils.make_point_srid(self.x, self.y)

    def to_geojson_point_srid(self, srid=None):
        return geo_utils.make_point_srid(self.x, self.y, srid)
