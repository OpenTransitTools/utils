from ott.utils.config_util import ConfigUtil
import validators
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


def get_realtime_feed_from_config(config=None):
    """ return the GTFS feed info from config
    """
    #import pdb; pdb.set_trace()
    ret_val = []
    if config is None:
        config = ConfigUtil(section='gtfs_realtime')

    feeds = config.get_json('feeds')
    for f in feeds:
        if 'agency_id' in f and len(f['agency_id']) > 0:
            ret_val.append(f)

    return ret_val


def get_realtime_url(name, feed, def_val):
    ret_val = def_val
    try:
        url = feed[name]
        if validators.url(url):
            ret_val = url
        else:
            log.debug("{} ({}) doesn't look like a url".format(url, name))
    except Exception, e:
        log.debug(e)
    return ret_val


def get_realtime_trips_url(feed, def_val=None):
    return get_realtime_url('trips', feed, def_val)


def get_realtime_alerts_url(feed, def_val=None):
    return get_realtime_url('alerts', feed, def_val)


def get_realtime_vehicles_url(feed, def_val=None):
    return get_realtime_url('vehicles', feed, def_val)

