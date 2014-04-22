from ott.utils import date_utils
from .param_parser import ParamParser

ROUTE_IDS=['route_id', 'routeID', 'routeId','route']
DIR_IDS=['dir', 'direction', 'direction_id', 'dir_id', 'directionID', 'dirID', 'directionId', 'dirId']

class RouteParamParser(ParamParser):
    def __init__(self, params):
        super(RouteParamParser, self).__init__(params)
        date_str = self._parse_date()
        self.date = date_utils.str_to_date(date_str)
        self.route_id = self.get_first_val(ROUTE_IDS + ['id']) 
        self.direction_id = self.get_first_val(DIR_IDS)
