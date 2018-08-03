from ott.utils import geo_utils
from ott.utils import num_utils


class Point(object):
    def __init__(self, x, y, radius=None):
        self.x = num_utils.to_float(x)
        self.y = num_utils.to_float(y)
        self.radius = num_utils.to_float(radius) # distance from the point

    def to_geojson(self):
        return geo_utils.make_geojson_point(self.x, self.y)

    def is_valid(self):
        return self.x and self.y

    def has_radius(self):
        return isinstance(self.radius, float)

    def to_geojson_point(self):
        return geo_utils.make_point_srid(self.x, self.y)

    def to_geojson_point_srid(self, srid=None):
        return geo_utils.make_point_srid(self.x, self.y, srid)
