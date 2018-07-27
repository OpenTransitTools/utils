from ott.utils import date_utils
from .param_parser import ParamParser


ROUTE_IDS = ['route_id', 'routeID', 'routeId', 'route', 'line']
DIR_IDS = ['dir', 'direction', 'direction_id', 'dir_id', 'directionID', 'dirID', 'directionId', 'dirId']


class RouteParamParser(ParamParser):
    def __init__(self, request):
        super(RouteParamParser, self).__init__(request)
        date_str = self._parse_date()
        self.date = date_utils.str_to_date(date_str)
        self.route_id = self.get_first_val_trim(ROUTE_IDS + ['id'])
        self.direction_id = self.get_first_val(DIR_IDS)

    def get_route_id(self, def_val=None):
        return self.route_id if self.route_id else def_val

    @classmethod
    def factory(cls, request):
        return RouteParamParser(request)
