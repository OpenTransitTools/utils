'''
'''
import re
import time
import datetime
import calendar
import logging
log = logging.getLogger(__file__)

from ott.utils import html_utils
from ott.utils import object_utils

class ParamParser(object):

    def __init__(self, request):
        self.request = request
        self.params = html_utils.params_to_dict(request)
        self.agency = self.get_first_val(['agency'], 'TriMet')
        self.detailed = self.get_first_val_as_bool(['detailed', 'full'], False)
        self.alerts = self.get_first_val_as_bool(['alerts', 'full'], False)
        self.query_string = None
        if type(self.params) == str:
            self.query_string = self.params
            self.params = self.query_str_to_params(self.params)


    def _parse_date(self):
        ''' parse out a date from either the 'date' param, or separate month/day/year params
            &month={month}&day={day}&year={year}
        '''
        self.date = self.get_first_val(['Date'])
        if self.date is None:
            self.date = self._make_date_from_parts()
        self._normalize_date_parts()
        return self.date


    def _make_date_from_parts(self, fmt="{year}-{month}-{day}"):
        ''' convert date 
        '''
        date = self.make_date_object(self.date)

        self.day = self.get_first_val(['Day'])
        if self.day is None:
            self.day = date.day

        self.month = self.get_first_val(['Month'])
        if self.month is None:
            self.month = date.month
        if type(self.month) == str and len(self.month) == 3:
            # make sure month is not an abbreviation, ala Jun
            for num, abbr in enumerate(calendar.month_abbr):
                if self.month == abbr:
                    self.month = num
                    break

        self.year  = self.get_first_val(['Year'])
        if self.year is None:
            self.year = date.year

        ret_val = fmt.format(**self.__dict__)
        return ret_val

    def _normalize_date_parts(self):
        ''' make sure we have all the date parts separated from the larger date field (since we build urls with that) 
        '''
        try:
            d = self.date.split('-')
            if self.year  is None:  self.year  = d[0]
            if self.month is None:  self.month = d[1]
            if self.day   is None:  self.day   = d[2]
        except:
            pass



    @classmethod
    def make_date_object(cls, date_str, fmt="%Y-%m-%d"):
        ''' will convert a date string into a date object ... or if that fails, return today's date
            note: you need to know the format of the date string -- default is year-month-day ala 2013-09-15
        '''
        try:
            ret_val = datetime.date.strptime(date_str, fmt)
        except:
            ret_val = datetime.date.today()
        return ret_val


    def _parse_time(self):
        ''' parse out a date from either the 'date' param, or separate month/day/year params
            &Hour={hour}&Min={min}&AmPm={am_pm}
        '''
        self.time = self.get_first_val(['Time'])
        if self.time is None:
            self.time = self._make_time_from_parts()
        self._normalize_time_parts()
        return self.time

    def _make_time_from_parts(self, fmt="{hour}:{min}{am_pm}", use_24_hour=False):
        ''' convert date 
        '''
        loc_time = self.make_time_object(self.time)

        self.hour = self.get_first_val(['Hour'])
        if self.hour is None:
            if use_24_hour:
                self.hour = time.strftime("%H", loc_time)
            else:
                self.hour = time.strftime("%I", loc_time)

        self.min = self.get_first_val(['Minute', 'Min'])
        if self.min is None:
            self.min = time.strftime("%M", loc_time)
        else:
            self.min = self.min.zfill(2)  # zero pad 2 places

        self.am_pm  = self.get_first_val(['am_pm', 'AmPm'])
        if self.am_pm is None:
            self.am_pm = time.strftime("%p", loc_time).lower()

        ret_val = fmt.format(**self.__dict__)
        return ret_val


    def _normalize_time_parts(self):
        ''' convert date 
        '''
        try:
            t = self.time.split(':')
            if self.hour  is None: self.hour  = t[0]
            if self.min   is None: self.min   = t[1][:2]
            if self.am_pm is None: self.am_pm = t[1][2:].strip()
        except:
            pass



    @classmethod
    def make_time_object(cls, time_str, fmt="%h:%M%a"):
        ''' will convert self.time into a time object ... or if that fails, return the local time
        '''
        try:
            ret_val = datetime.time.strptime(time_str, fmt)
        except:
            ret_val = time.localtime()
        return ret_val


    def param_exists(self, param):
        return param in self.params


    def get(self, name, def_val=None):
        '''
        '''
        ret_val = def_val
        try:
            ret_val = self.params[name]
        except:
            try:
                ret_val = self.params[name.lower()]
            except:
                pass

        return ret_val


    def get_first_val(self, names, def_val=None):
        ''' pass in a list of 'names', and return the first name that has a value in self.params
        '''
        ret_val = def_val
        for n in names:
            v = self.get(n)
            if v is not None and v != 'None':
                ret_val = v
                break
        return ret_val


    def get_first_val_as_numeric(self, names, def_val=None):
        ''' pass in a list of 'names', and return the first name that has a value in self.params
            with the additional requirement that this value is a numeric value 
        '''
        ret_val = None
        str = def_val
        try:
            str = self.get_first_val(names)
            ret_val = float(str)
        except:
            ret_val = str
        return ret_val

    def get_first_val_as_int(self, names, def_val=None):
        ''' pass in a list of 'names', and return the first name that has a value in self.params
            with the additional requirement that this value is an int value 
        '''
        ret_val = def_val
        try:
            ret_val = self.get_first_val(names)
        except:
            pass
        return ret_val


    def get_first_val_as_bool(self, names, def_val=False):
        ''' pass in a list of 'names', and return the first name that has a value in self.params
            with the additional requirement that this value is an int value 
        '''
        ret_val = def_val
        try:
            val = self.get_first_val(names)
            if val == '':
                val = 'T'
            #import pdb; pdb.set_trace()
            if not any(f in val for f in ('false', 'False', 'None')):
                ret_val = True
            else:
                ret_val = False
        except:
            pass
        return ret_val


    @classmethod
    def query_str_to_params(cls, qs):
        ret_val = {}
        params = qs.split('&')
        for p in params:
            q = p.split('=')
            if len(q) == 2:
                ret_val[q[0]] = q[1]
            elif len(q) == 1:
                ret_val[q[0]] = True
        return ret_val


    @classmethod
    def strip_coord(cls, place):
        ''' break up any PLACE::45.5,-122.5 into name & coord part
            (if no ::, then coord is assumed to be whole input string) 
        '''
        ret_val = place
        try:
            parts = place.split("::")
            ret_val = parts[0]
        except Exception as ex:
            log.warning(ex)
        return ret_val


    @classmethod
    def has_valid_coord(cls, coord):
        '''
        '''
        ret_val = False

        try:
            # break up any PLACE::45.5,-122.5 into name & coord part 
            # (if no ::, then coord is assumed to be whole input string)
            parts = coord.split("::")
            if len(parts) > 1:
                coord = parts[1]
    
            if coord:
                regex = re.match("[0-9]{1,3}.[0-9]+[&#16|,|\s]+-?[0-9]{1,3}.[0-9]+", coord)
                if regex:
                    ret_val = True
        except Exception as ex:
            log.warning(ex)

        return ret_val


    @classmethod
    def make_named_coord(cls, name, coord=None, def_val=None):
        '''
        '''
        ret_val = def_val

        if name and coord:
            ret_val = "{0}::{1}".format(object_utils.to_str(name), coord)
        elif name:
            ret_val = name
        elif coord:
            ret_val = coord

        return ret_val


    @classmethod
    def to_int(cls, str, def_val=0):
        ret_val = def_val
        try:
            ret_val = int(str)
        except:
            pass
        return ret_val

