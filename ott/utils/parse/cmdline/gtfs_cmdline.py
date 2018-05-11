import db_cmdline

import logging
log = logging.getLogger(__file__)


def blank_parser(prog_name='bin/gtfs'):
    """
    create a generic database commandline arg PARSER
    """
    import argparse
    parser = argparse.ArgumentParser(
        prog=prog_name,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    return parser


def agency_option(parser, required=False, def_val='agency_id', help_msg="GTFS agency id (i.e., might also be a db schema name)"):
    parser.add_argument(
        '--agency',
        '-agency',
        '-a',
        required=required,
        default=def_val,
        help=help_msg
    )


def route_option(parser, required=False, def_val=None, help_msg="GTFS route id"):
    parser.add_argument(
        '--route_id',
        '-route',
        '-rt',
        required=required,
        default=def_val,
        help=help_msg
    )


def stop_option(parser, required=False, def_val=None, help_msg="GTFS stop id"):
    parser.add_argument(
        '--stop_id',
        '-stop',
        '-st',
        required=required,
        default=def_val,
        help=help_msg
    )


def api_key(parser, required=False, help_msg=None):
    if help_msg is None:
        help_msg = "api key needed to access this data"

    parser.add_argument(
        '--api_key',
        '-akey',
        '-ak',
        required=required,
        help=help_msg
    )


def gtfs_parser():
    """ create a generic database commandline arg PARSER """
    parser = db_cmdline.db_parser('bin/load_gtfs')
    agency_option(parser, True)
    parser.add_argument(
        '--url',
        '-url',
        '-u',
        required=True,
        help="url to gtfs feed (ala https://developers.google.com/transit/gtfs/examples/sample-feed.zip)"
    )
    return parser


def gtfs_rt_parser(api_key_required=False, api_key_msg=None):
    """ create a generic database commandline arg PARSER """
    parser = db_cmdline.db_parser('bin/load_gtfs_rt')
    agency_option(parser, True)
    if api_key_required:
        api_key(parser, api_key_required, api_key_msg)
    parser.add_argument(
        '--alerts_url',
        '-aurl',
        '-al',
        required=False,
        help="url to gtfs-realtime *alerts* data feed"
    )
    parser.add_argument(
        '--trips_url',
        '-turl',
        '-t',
        required=False,
        help="url to gtfs-realtime *trip updates* data feed"
    )
    parser.add_argument(
        '--vehicles_url',
        '-vurl',
        '-v',
        required=False,
        help="url to gtfs-realtime *vehicle positions* data feed"
    )

    return parser