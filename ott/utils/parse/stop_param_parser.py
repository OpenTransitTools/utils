'''
'''
from ott.utils import object_utils
from param_parser import ParamParser

class StopParamParser(ParamParser):

    def __init__(self, params):
        super(StopParamParser, self).__init__(params)
        date_str = self._parse_date()
        self.date = object_utils.str_to_date(date_str)
        self.stop_id = self.get_first_val(['stop_id', 'stopID',  'stopId', 'stop', 'Loc', 'loc']) 
        self.route_id = self.get_first_val(['route_id', 'routeID', 'routeId','route']) 
        self.direction_id = self.get_first_val(['dir', 'direction', 'direction_id', 'dir_id', 'directionID', 'dirID', 'directionId', 'dirId']) 
