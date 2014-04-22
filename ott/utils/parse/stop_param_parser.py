from ott.utils import date_utils
from .param_parser import ParamParser
from .route_param_parser import ROUTE_IDS, DIR_IDS

STOP_IDS = ['stop_id', 'stopID',  'stopId', 'stop', 'Loc', 'loc'] 

class StopParamParser(ParamParser):

    def __init__(self, params):
        super(StopParamParser, self).__init__(params)
        date_str = self._parse_date()
        self.date = date_utils.str_to_date(date_str)
        self.stop_id = self.get_first_val(STOP_IDS + ['id'])
        self.route_id = self.get_first_val(ROUTE_IDS) 
        self.direction_id = self.get_first_val(DIR_IDS)
