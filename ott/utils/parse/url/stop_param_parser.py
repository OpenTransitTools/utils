from ott.utils import date_utils
from .param_parser import ParamParser
from .route_param_parser import ROUTE_IDS, DIR_IDS

STOP_IDS = ['stop_id', 'stopID',  'stopId', 'stop', 'Loc', 'locID', 'loc1'] 


class StopParamParser(ParamParser):
    def __init__(self, request):
        super(StopParamParser, self).__init__(request)
        self.date_str = self._parse_date()
        self.date = date_utils.str_to_date(self.date_str)
        self.stop_id = self.get_first_val_trim(STOP_IDS + ['id'])
        self.route_id = self.get_first_val_trim(ROUTE_IDS) 
        self.direction_id = self.get_first_val(DIR_IDS)

    def get_stop_id(self, def_val=None):
        return self.stop_id if self.stop_id else def_val

    def get_route_id(self, def_val=None):
        return self.route_id if self.route_id else def_val

    @classmethod
    def factory(cls, request):
        return StopParamParser(request)
