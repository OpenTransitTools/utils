from ott.utils import geo_utils

import simplejson as json
import datetime

import logging
log = logging.getLogger(__file__)



class SerializerRegistry(object):
    """ @see: http://stackoverflow.com/questions/4821940/how-to-make-simplejson-serializable-class
        this class will help serialize abitrary python objects into JSON (along with date / datetime handelling)
    """
    def __init__(self):
        self._classes = {}

    def add(self, cls):
        self._classes[cls.__module__, cls.__name__] = cls
        return cls

    def object_hook(self, dct):
        module, cls_name = dct.pop('__type__', (None, None))
        if cls_name is not None:
            return self._classes[module, cls_name].from_dict(dct)
        else:
            return dct

    def default(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            # simple / stupid handling of date and datetime object serialization
            return str(obj)
        else:
            dct = obj.to_dict()
            dct['__type__'] = [type(obj).__module__, type(obj).__name__]
            return dct

registry = SerializerRegistry()


@registry.add
class MinimalDao(object):
    def to_dict(self):
        return self.__dict__

    def to_json(self, pretty=False):
        return self.obj_to_json(self, pretty)

    def from_json(self, str):
        return json.loads(str, object_hook=registry.object_hook)

    def parse_json(self, json):
        pass

    @classmethod
    def parse_geojson(self, geojson):
        return geo_utils.parse_geojson(geojson)

    @classmethod
    def geom_to_geojson(cls, session, geom):
        geojson = None
        try:
            #import pdb; pdb.set_trace()
            import geoalchemy2.functions as func
            geojson = session.scalar(func.ST_AsGeoJSON(geom))
        except:
            log.warn("couldn't get geojson data from geom column")
        return geojson

    @classmethod
    def orm_to_geojson(cls, orm):
        """ export orm column 'geom'
        """
        geojson = None
        try:
            geojson = cls.geom_to_geojson(orm.session, orm.geom)
        except:
            log.warn("couldn't get geojson data from orm object")
        return geojson

    @classmethod
    def obj_to_json(cls, obj, pretty=False):
        if pretty:
            ret_val = json.dumps(obj, default=registry.default, indent=4, sort_keys=True)
        else:
            ret_val = json.dumps(obj, default=registry.default)
        return ret_val

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)

    @classmethod
    def format_template_from_dict(cls, dict, template):
        ret_val = template
        try:
            ret_val = template.format(**dict)
        except:
            pass
        return ret_val


@registry.add
class BaseDao(MinimalDao):

    def __init__(self):
        # TODO: should we call a method to set these variables, so that it's done in a single place, rather than return this multiple times?
        #       self.set_date()
        self.status_code = 200
        self.status_message = None
        self.has_errors = False

        # todo: strange that alerts and dates stuff here here (some just added ... but trying to find why alerts are getting 'stuck')
        self.has_alerts = False
        self.alerts = []
        self.date_info = {}

    def __repr__(self):
        return str(self.__dict__)

    def set_date(self, date=None):
        #import pdb; pdb.set_trace()
        if not hasattr(self, 'date_info'):
            self.date_info = {}
        if date is None or not hasattr(date, 'month') or not hasattr(date, 'day'):
            date = datetime.date.today()
        self.date_info['month'] = date.month
        self.date_info['day'] = date.day

    def set_alerts(self, alerts):
        self.alerts = alerts
        if self.alerts and len(self.alerts) > 0:
            self.has_alerts = True
        else:
            self.has_alerts = False


class DatabaseNotFound(BaseDao):
    def __init__(self):
        super(DatabaseNotFound, self).__init__()
        self.status_code = 404
        self.status_message = 'Data not found'
        self.has_errors = True


class ServerError(BaseDao):
    def __init__(self):
        super(ServerError, self).__init__()
        self.status_code = 500
        self.status_message = 'Server error ... please try again later'
        self.has_errors = True
