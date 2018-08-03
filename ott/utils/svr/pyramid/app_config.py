from ott.utils import db_utils

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
            log.warn(e)

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