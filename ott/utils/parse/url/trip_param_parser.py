from .param_parser import ParamParser
from ott.utils.config_util import ConfigUtil
from ott.utils import object_utils

import logging
log = logging.getLogger(__file__)


class TripParamParser(ParamParser):
    def __init__(self, request):
        super(TripParamParser, self).__init__(request)

        # import pdb; pdb.set_trace()
        config = ConfigUtil.factory(section="otp")

        self.frm   = None
        self.to    = None
        self._parse_from()
        self._parse_to()

        self.max_hours = config.get_int('otp_max_hours', def_val=6)
        self._parse_date()
        self._parse_time()

        self.arrive_depart_raw = None
        self.arrive_depart = None
        self.optimize    = None
        self.walk        = None
        self.walk_meters = 0.0
        self.mode        = None
        self.banned_routes = None
        self._parse_arrive_depart()
        self._parse_optimize()
        self._parse_walk()
        self._parse_mode()
        self._parse_misc()

    @classmethod
    def factory(cls, request):
        return TripParamParser(request)

    def clone(self):
        """ copy this parser
        """
        p = super(TripParamParser, self).clone()
        p.frm = self.frm
        p.to = self.to
        p.max_hours = self.max_hours
        p.arrive_depart_raw = self.arrive_depart_raw
        p.arrive_depart = self.arrive_depart
        p.optimize = self.optimize
        p.walk = self.walk
        p.walk_meters = self.walk_meters
        p.mode = self.mode
        return p

    def safe_format(self, fmt, def_val=''):
        """ 
        """
        ret_val = def_val
        try:
            ret_val = fmt.format(**self.__dict__)
        except UnicodeEncodeError as e:
            log.debug(e)
            log.debug('trying to fix the encoding with the frm & to coords')
            self.frm = object_utils.to_str(self.frm)
            self.to = object_utils.to_str(self.to)
            try:
                ret_val = fmt.format(**self.__dict__)
            except:
                pass
        except Exception as e:
            log.debug(e)
        return ret_val

    def pretty_output(self):
        return self.param_exists('pretty') or self.param_exists('is_pretty')

    def ott_url_params(self, fmt="from={frm}&to={to}&Hour={hour}&Minute={min}&AmPm={am_pm}&month={month}&day={day}&year={year}&Walk={walk}&Arr={arrive_depart_raw}&min={optimize}&mode={mode}"):
        """ return a string with the parameter values formatted for the OTT webapps
        """
        ret_val = self.safe_format(fmt)
        ret_val = object_utils.fix_url(ret_val)
        return ret_val

    def add_banned_routes_param(self, url_params, banned_param="bannedRoutes"):
        ret_val = url_params
        if self.banned_routes:
            ret_val = "{}&{}={}".format(ret_val, banned_param, self.banned_routes)
        return ret_val

    def ott_url_params_return_trip(self, add_hours=1, add_mins=30, fmt="from={to}&to={frm}&month={month}&day={day}&year={year}&Walk={walk}&Arr={arrive_depart_raw}&min={optimize}&mode={mode}"):
        """ return a string with the parameter values formatted for OTT with a return trip of hours+X and minutes+Y 
            (change am to pm if needed, etc...)
        """
        fmt = "Hour={add_hour}&Minute={add_min}&AmPm={add_am_pm}&" + fmt

        # handle the extra minutes for the reverse trip (increment hours if need be)
        self.add_min = self.to_int(self.min) + add_mins
        if self.add_min > 60:
            self.add_min = self.to_int(self.add_min % 60)
            add_hours += 1

        # handle the extra hours (change am / pm if we go past 12 hour mark)
        self.add_am_pm = self.am_pm
        self.add_hour = self.to_int(self.hour) + add_hours
        if self.add_hour > 12:
            self.add_hour = self.add_hour - 12
            if self.add_am_pm == 'pm':
                self.add_am_pm = 'am'
            else:
                self.add_am_pm = 'pm'

        ret_val = self.safe_format(fmt)
        ret_val = object_utils.fix_url(ret_val)
        return ret_val

    def otp_url_params(self, fmt="fromPlace={frm}&toPlace={to}&time={time}&date={date}&mode={mode}&optimize={optimize}&maxWalkDistance={walk_meters}&arriveBy={arrive_depart}"):
        """ return a string with the parameter values formatted for the OTP routing engine (opentripplanner-api-webapp)
        """
        # import pdb; pdb.set_trace()
        ret_val = self.safe_format(fmt)
        ret_val = ret_val.replace("False", "false").replace("True", "true")
        ret_val = self.add_banned_routes_param(ret_val)
        ret_val = object_utils.fix_url(ret_val)
        return ret_val

    def map_url_params(self, fmt="from={frm}&to={to}&time={time}&date={month}/{day}/{year}&mode={mode}&optimize={optimize}&maxWalkDistance={walk_meters:.0f}&arriveBy={arrive_depart}"):
        """ return a string with the parameter values formatted for the OTT webapps
            http://maps.trimet.org/prod?
                to=ZOO%3A%3A45.509700%2C-122.716290
                from=PDX%3A%3A45.587647%2C-122.593173
                time=5%3A30%20pm
                date=6/13/2013
                mode=TRANSIT%2CWALK
                optimize=QUICK
                maxWalkDistance=420
                arriveBy=true
        """
        ret_val = self.safe_format(fmt)
        ret_val = ret_val.replace("False", "false").replace("True", "true")
        ret_val = object_utils.fix_url(ret_val)
        return ret_val

    def mod_url_params(self, fmt="fromPlace={frm}&toPlace={to}&optimize={optimize}&arriveBy={arrive_depart}&time={time}"):
        """ return a string with the parameter values formatted for the OTT webapps
            https://modbeta.trimet.org/map/#/
                toPlace=ZOO%3A%3A45.509700%2C-122.716290
                fromPlace=PDX%3A%3A45.587647%2C-122.593173
                time=5%3A30%20pm
                date=2013-06-13
                mode=WALK,BUS,TRAM,RAIL,GONDOLA
                optimize=QUICK
                maxWalkDistance=420
                arriveBy=true
        """
        ret_val = self.safe_format(fmt)
        mode = self.to_mod_mode()
        dist = self.to_mod_distance()
        mod_date = "date={}-{}-{}".format(self.year, str(self.month).zfill(2), str(self.day).zfill(2))
        ret_val = "{}&{}&mode={}&maxWalkDistance={}".format(ret_val, mod_date, mode, dist)
        ret_val = ret_val.replace("False", "false").replace("True", "true")
        ret_val = object_utils.fix_url(ret_val)
        return ret_val

    def get_itin_num(self, def_val="1"):
        ret_val = def_val
        if 'itin_num' in self.params:
            ret_val = self.params['itin_num']
        return ret_val

    def get_itin_num_as_int(self, def_val=1):
        ret_val = self.get_itin_num()
        try:
            ret_val = self.to_int(ret_val)
        except: 
            log.info("params['itin_num'] has a value of {0} (it's not parsing into an int)".format(ret_val))
            ret_val = def_val
        return ret_val 

    def get_from(self, def_val=None):
        ret_val = def_val
        if self.frm:
            ret_val = self.frm 
        return ret_val

    def set_from(self, val):
        if val:
            self.frm = val

    def get_to(self, def_val=None):
        ret_val = def_val
        if self.to:
            ret_val = self.to 
        return ret_val

    def set_to(self, val):
        if val:
            self.to = val

    def get_arrive_param(self):
        """"""
        return self.get_first_val(['Arr'])

    def is_arriveby(self, arr=None):
        """"""
        ret_val = False
        if arr is None:
            arr = self.get_arrive_param()
        if arr in ('A', 'Arr', 'Arrive', 'True', 'true'):
            ret_val = True
        return ret_val

    def is_latest(self, arr=None):
        """"""
        ret_val = False
        if arr is None:
            arr = self.get_arrive_param()
        if arr in ('L', 'Late', 'Latest'):
            ret_val = True
        return ret_val

    def is_earliest(self, arr=None):
        """"""
        ret_val = False
        if arr is None:
            arr = self.get_arrive_param()
        if arr in ('E', 'Early', 'Earliest'):
            ret_val = True
        return ret_val

    def _parse_from(self):
        """
        parse out the trip origin from get params ... the value could be a string, a coordinate or combo of the two
        """
        name = self.get_first_val(['from', 'fromPlace', 'f'])
        if name:
            self.frm = object_utils.to_str(name)
            pos = name.find('::')
            if pos < 0 or pos - 2 >= len(name):
                coord = self.get_first_val(['fromCoord'])
                if coord:
                    self.frm = self.make_named_coord(name, coord)
                else:
                    lat = self.get_first_val(['fromLat', 'fLat'])
                    lon = self.get_first_val(['fromLon', 'fLon'])
                    if lat and lon:
                        coord = "{0},{1}".format(lat, lon)
                        self.frm = self.make_named_coord(name, coord)

            # escape the string
            self.frm = self.frm.replace("&", "%26")  # escape & in the name

    def _parse_to(self):
        """
        parse out the trip destination from get params ... the value could be a string,a coordinate or combo of the two
        """
        name = self.get_first_val(['to', 'toPlace', 't'])
        if name:
            self.to = object_utils.to_str(name)
            pos = name.find('::')
            if pos < 0 or pos - 2 >= len(name):
                coord = self.get_first_val(['toCoord'])
                if coord:
                    self.to = self.make_named_coord(name, coord)
                else:
                    lat = self.get_first_val(['toLat', 'tLat'])
                    lon = self.get_first_val(['toLon', 'tLon'])
                    if lat and lon:
                        coord = "{0},{1}".format(lat, lon)
                        self.to = self.make_named_coord(name, coord)

            # escape the string
            self.to = self.to.replace("&", "%26")  # escape & in the name

    def _parse_walk(self):
        """ parse out the max walk (bike) distance ... default to 1 mile (~1609 meters)
        """
        self.walk = self.get_first_val(['maxWalkDistance', 'maxWalk', 'Walk'], "1609")
        try:
            dist = float(self.walk)
            self.walk_meters = dist

            # self.walk value of less than 11 implies this is a fraction of a mile
            # (note OTP values are in meters, thus 1609 = number of meters in a mile)
            if dist <= 10.0:
                self.walk_meters = 1609 * dist
        except:
            pass

    def _parse_arrive_depart(self):
        """ parse out the arrive / depart string
        """
        self.arrive_depart = False
        val = self.get_arrive_param()
        if val:
            self.arrive_depart_raw = val
            if self.is_arriveby(val):
                self.arrive_depart = True
            elif self.is_latest(val):
                self.arrive_depart = True
                self.time = "1:30am"
            elif self.is_earliest(val):
                self.arrive_depart = False
                self.time = "4:00am"

    def _parse_misc(self):
        """ parse everything else for a param"""
        mh = self.get_first_val_as_int(['maxHours'])
        if mh:
            self.max_hours = mh

    def _parse_optimize(self):
        """ parse out the optimize flag
        """
        self.optimize = self.get_first_val(['Optimize', 'Opt', 'Min'])
        if self.optimize in ('F', 'X', 'TRANSFERS'):
            self.optimize = 'TRANSFERS'
        elif self.optimize in ('S', 'SAFE'):
            self.optimize = 'SAFE'
        else:
            self.optimize = 'QUICK'

    def _parse_mode(self):
        """ parse out the mode string ... and default to TRANSIT,WALK
            convert mode string, if it's legacy, to OTP mode strings
        """
        self.mode = self.get_first_val(['Mode'])

        # order is important....
        if self.mode is None:
            self.mode = 'TRANSIT,WALK'
        elif self.mode == 'WALK':
            self.mode = 'WALK'
        elif ('TRANS' in self.mode or ('RAIL' in self.mode and 'BUS' in self.mode)) and 'BIC' in self.mode:
            self.mode = 'TRANSIT,BICYCLE'
        elif ('TRAIN' in self.mode or 'RAIL' in self.mode) and 'BIC' in self.mode:
            self.mode = 'RAIL,TRAM,SUBWAY,FUNICULAR,GONDOLA,BICYCLE'
        elif 'BUS' in self.mode and 'BIC' in self.mode:
            self.mode = 'BUS,BICYCLE'
        elif self.mode == 'BIKE' or self.mode =='BICYCLE':
            self.mode = 'BICYCLE'
        elif self.mode in ('B', 'BUS', 'BUSISH', 'BUSISH,WALK', 'BUS,WALK'):
            self.mode = 'BUS,WALK'
        elif self.mode in ('T', 'TRAIN', 'TRAINISH', 'TRAINISH,WALK') or 'RAIL' in self.mode:
            self.mode = 'RAIL,TRAM,SUBWAY,FUNICULAR,GONDOLA,WALK'
        elif 'CAR' in self.mode:
            pass # hope this works...
        else:
            log.info("don't recoginize this mode -- so changing self.mode from '{}' to the default 'TRANSIT,WALK'".format(self.mode))
            self.mode = 'TRANSIT,WALK'

    def to_mod_mode(self):
        """
        parse out the mode string for the MOD map...
        """
        transit_mode = 'BUS,TRAM,RAIL,GONDOLA'
        rail_mode = 'TRAM,RAIL,GONDOLA'
        def_mode = 'WALK,' + transit_mode

        # order is important....
        if self.mode is None:
            ret_val = def_mode
        elif self.mode == 'TRANSIT,WALK':
            ret_val = def_mode
        elif self.mode == 'WALK':
            ret_val = 'WALK'
        elif ('TRANS' in self.mode or ('RAIL' in self.mode and 'BUS' in self.mode)) and 'BIC' in self.mode:
            ret_val = 'BICYCLE,' + transit_mode
        elif ('TRAIN' in self.mode or 'RAIL' in self.mode) and 'BIC' in self.mode:
            ret_val = 'BICYCLE,' + rail_mode
        elif 'BUS' in self.mode and 'BIC' in self.mode:
            ret_val = 'BICYCLE,BUS'
        elif self.mode == 'BIKE' or self.mode =='BICYCLE':
            ret_val = 'BICYCLE'
        elif self.mode in ('B', 'BUS', 'BUSISH', 'BUSISH,WALK', 'BUS,WALK'):
            ret_val = 'WALK,BUS'
        elif self.mode in ('T', 'TRAIN', 'TRAINISH', 'TRAINISH,WALK') or 'RAIL' in self.mode:
            ret_val = 'WALK,' + rail_mode
        elif 'CAR' in self.mode:
            ret_val = 'WALK,' + transit_mode + ',CAR_PARK'
        else:
            log.info("don't recoginize this mode -- so changing to default mode {}".format(self.mode, def_mode))
            ret_val = def_mode
        return ret_val

    def to_mod_distance(self):
        """
        mod uses different lenghts than what other systems use (such precision)
        """
        ret_val = self.walk
        if self.walk == "160":
            ret_val = "160.9"
        elif self.walk == "420":
            ret_val = "402.3"
        elif self.walk == "840":
            ret_val = "804.7"
        elif self.walk == "1260":
            ret_val = "1207"
        elif self.walk == "1609":
            ret_val = "1609"
        elif self.walk == "3219":
            ret_val = "3219"
        elif self.walk == "8047":
            ret_val = "8047"
        elif self.walk == "16093":
            ret_val = "16093"
        else:
            ret_val = "1207"
        return ret_val