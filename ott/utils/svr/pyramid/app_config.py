import logging
log = logging.getLogger(__file__)


class AppConfig(object):
    """
    this class contains settings and configs for a Pyramid web app
    create this on the main() entry
    see setup.py entry points + config/*.ini [app:main] ala pserve (e.g., bin/pserve config/development.ini)
    """
    config = None
    pyramid = None
    wsgi_app = None
    db = None

    def __init__(self, **config):
        # import pdb; pdb.set_trace()
        self.config = config

        # step 1: enable pyamid config
        from pyramid.config import Configurator
        self.pyramid = Configurator(settings=config)

        # step 2: enable logging from settings
        try:
            # logging config for pserve / wsgi
            if config and 'logging_config_file' in config:
                from pyramid.paster import setup_logging
                setup_logging(config['logging_config_file'])
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

    def set_db(self, db):
        """ ability to pass around db connection variable to view, etc... """
        self.db = db

    def get_db(self):
        return self.db