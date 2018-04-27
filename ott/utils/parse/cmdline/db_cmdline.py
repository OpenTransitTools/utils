import logging
log = logging.getLogger(__file__)


def db_parser(prog_name='bin/load_db', tables=['Could be (Decarative) Base.metadata.sorted_tables']):
    """ create a generic database commandline arg PARSER """
    import argparse
    parser = argparse.ArgumentParser(
        prog=prog_name,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--database_url',
        '-d',
        required=True,
        help="(geo) database url ala dialect+driver://user:password@host/dbname[?key=value..]"
    )
    parser.add_argument(
        '--schema',
        '-schema',
        '-s',
        help="database schema"
    )
    parser.add_argument(
        '--is_geospatial',
        '-geo',
        '-g',
        action="store_true",
        help="add geometry columns"
    )
    parser.add_argument(
        '--create',
        '-create',
        '-c',
        action="store_true",
        help="drop / create database tables for vehicles"
    )
    parser.add_argument(
        '--clear',
        '-clear',
        '-cf',
        action="store_true",
        help="clear table(s) before loading"
    )
    parser.add_argument(
        '--tables',
        choices=tables, default=None, nargs='*',
        help="Limited list of TABLES to load, if blank, load all tables"
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
    parser = db_parser('bin/load_gtfs')
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
    parser = db_parser('bin/load_gtfs_rt')
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