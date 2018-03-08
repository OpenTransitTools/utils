import logging
log = logging.getLogger(__file__)


def db_args(prog_name='db loader'):
    """ create a generic database commandline arg PARSER """
    import argparse
    parser = argparse.ArgumentParser(
        prog=prog_name,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--database_url',
        '-d',
        required='true',
        help="(geo) database url ala dialect+driver://user:password@host/dbname[?key=value..]"
    )
    parser.add_argument(
        '--schema',
        '-schema',
        '-s',
        help="database schema"
    )
    parser.add_argument(
        '--geo',
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
    return parser


def gtfs_parser():
    """ create a generic database commandline arg PARSER """
    parser = db_args()
    parser.add_argument(
        '--agency',
        '-agency',
        '-a',
        default="trimet",
        help="agency name (string)"
    )
    parser.add_argument(
        '--url',
        '-url',
        '-u',
        required='true',
        help="url to gtfs-realtime data"
    )
    return parser

