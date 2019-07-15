from ott.utils import db_utils
from ott.utils.parse.url.param_parser import SimpleParamParser

import logging
log = logging.getLogger(__file__)


class AppConfig(object):
    """
    this class contains settings and configs for a Pyramid web app
    create this on the main() entry
    see setup.py entry points + config/*.ini [app:main] ala pserve (e.g., bin/pserve config/development.ini)
    """
    ini_settings = None
    pyramid = None
    wsgi_app = None
    _db = None

    def __init__(self, **ini_settings):
        # import pdb; pdb.set_trace()
        self.ini_settings = ini_settings  # variables from your project's config/*.ini file

        # step 1: enable pyamid config
        from pyramid.config import Configurator
        self.pyramid = Configurator(settings=ini_settings)

        # step 2: enable logging from settings
        try:
            # logging config for pserve / wsgi
            if ini_settings and 'logging_config_file' in ini_settings:
                from pyramid.paster import setup_logging
                setup_logging(ini_settings['logging_config_file'])
        except Exception as e:
            log.warning(e)

        # step 3: enable cors
        if ini_settings and ini_settings.get('pyramid.debug_all', 'false').startswith('true'):
            self.add_cors_headers()

    def make_wsgi_app(self):
        """
        this function returns a Pyramid WSGI application.
        """
        if self.wsgi_app is None:
            self.wsgi_app = self.pyramid.make_wsgi_app()
        return self.wsgi_app

    def config_include_scan(self, clazz):
        # step 1: assume that view.set_app_config(AppConfig instance) exists so we can pass the config on to view
        #         and warn us if that's not the case
        try:
            clazz.set_app_config(self)
        except Exception as e:
            log.info(e)

        # step 2: also assume that this object / modules class has a do_view_config() method where views are created
        self.pyramid.include(clazz.do_view_config)

        # step 3: finally, scan this view class for attributes to config view endpoints
        self.pyramid.scan(clazz.__name__)

    def add_cors_headers(self, timeout=None):
        """
        set the CORS headers so that this app can serve AJAX calls from a different domain that the calling app
        :param timeout: optional parameter to set 'Access-Control-Max-Age' from the default 1728000 value
        """
        if timeout:
            from .app_utils import set_max_age
            set_max_age(timeout)

        from pyramid.events import NewRequest
        from .app_utils import add_cors_headers_response_callback
        self.pyramid.add_subscriber(add_cors_headers_response_callback, NewRequest)

    def get_url_param(self):
        """
        this function returns a Pyramid WSGI application.
        """
        if self.wsgi_app is None:
            self.wsgi_app = self.pyramid.make_wsgi_app()
        return self.wsgi_app

    def get_agency(self, url_params=None, def_val=None):
        """
        agency can be passed thru URL
        default agency can also be configured in the .ini file
        this routine will do a variety of checks for agency
        """
        ret_val = def_val
        try:
            # step 1: get the agency id from the .ini file (as a default)
            def_agency = self.ini_settings.get('agency_id')

            # step 2: if we were sent either url params or a request object, check that for a default override
            if url_params:
                # step 2a: make sure we have a param parser
                if not isinstance(url_params, SimpleParamParser):
                    url_params = SimpleParamParser(url_params)

                # step 2b: get agency from URL or .ini file, and return it
                agency = url_params.get_first_val(['agency', 'agency_id'], def_agency)
                if agency:
                    ret_val = agency
        except Exception as e:
            log.info(e)
        return ret_val

    @property
    def db(self):
        return self._db

    def set_db(self, db):
        """ ability to pass around db connection variable to view, etc... """
        self._db = db

    def db_params_from_config(self):
        return db_utils.db_params_from_config(self.ini_settings)

    def gtfsdb_param_from_config(self):
        return db_utils.gtfsdb_param_from_config(self.ini_settings)
