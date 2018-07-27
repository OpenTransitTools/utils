from ott.utils import geo_utils


class Coord(object):
    def __init__(self, x, y, radius=None):
        self.x = x
        self.y = y
        self.radius = radius # distance from the point

    def to_geojson_point(self):
        return geo_utils.make_point_srid(self.x, self.y)

    def to_geojson_point_srid(self, srid=None):
        return geo_utils.make_point_srid(self.x, self.y, srid)
