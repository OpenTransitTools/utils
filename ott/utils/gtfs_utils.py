
from ott.utils.config_util import ConfigUtil

import logging
log = logging.getLogger(__file__)


def get_feeds_from_config(config=None):
    """ return the GTFS feed info from config
    """
    if config is None:
        config = ConfigUtil(section='gtfs')

    feeds = config.get_json('feeds')
    return feeds


def get_schema_name_from_feed(feed, def_name="OTT"):
    """ get a name for the database schema (amoungst other systems)
        either the feed config will have a
    """
    name = def_name
    if 'schema' in feed:
        name = feed['schema']
    else:
        name = feed['name'].rstrip(".zip").lower()
    return name

