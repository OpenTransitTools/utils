import logging
log = logging.getLogger(__file__)


class AppConfig(object):

    # cache time - affects how long varnish cache will hold a copy of the data
    cache_long = 36000  # 10 hours
    cache_short = 600   # 10 minutes

    settings = None
    config = None
    wsgi_app = None

    def __init__(self, **settings):
        self.settings = settings

        # step 1: enable pyamid config
        from pyramid.config import Configurator
        self.config = Configurator(settings=settings)

        # step 2: enable logging from settings
        try:
            # logging config for pserve / wsgi
            if settings and 'logging_config_file' in settings:
                from pyramid.paster import setup_logging
                setup_logging(settings['logging_config_file'])
        except Exception as e:
            log.warn(e)

    def make_wsgi_app(self):
        """
        this function returns a Pyramid WSGI application.
        """
        if self.wsgi_app is None:
            self.wsgi_app = self.config.make_wsgi_app()
        return self.wsgi_app

    def config_include_scan(self, clazz):
        self.config.include(clazz.do_view_config)
        self.config.scan(clazz.__name__)


