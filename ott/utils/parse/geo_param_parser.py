from .param_parser import ParamParser

NAME_IDS = ['name', 'desc']
NUM_IDS  = ['num',  'count', 'limit']
LON_IDS  = ['x',    'lon']
LAT_IDS  = ['y',    'lat']


class GeoParamParser(ParamParser):

    def __init__(self, params, def_count=10):
        super(GeoParamParser, self).__init__(params)
        self.limit = self.get_first_val(NUM_IDS, def_count)
        self.name  = self.get_first_val(NAME_IDS)
        self.lat   = self.get_first_val(LAT_IDS) 
        self.lon   = self.get_first_val(LON_IDS)

    def has_coords(self):
        ret_val = False
        if self.lat and self.lon:
            ret_val = True
        return ret_val

    def to_point(self):
        point = 'POINT({0} {1})'.format(self.lon, self.lat)
        return point

    def to_point_srid(self, srid='4326'):
        ret_val = 'SRID={0};{1}'.format(srid, self.to_point())
        return ret_val
