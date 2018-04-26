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


def agency_option(parser, def_val='trimet'):
    parser.add_argument(
        '--agency',
        '-agency',
        '-a',
        default=def_val,
        help="agency name (string)"
    )


def gtfs_parser():
    """ create a generic database commandline arg PARSER """
    parser = db_parser('bin/load_gtfs')
    agency_option(parser)
    parser.add_argument(
        '--url',
        '-url',
        '-u',
        required='true',
        help="url to gtfs (or gtfs-realtime) data"
    )
    return parser


def gtfs_rt_parser():
    """ create a generic database commandline arg PARSER """
    parser = db_parser('bin/load_gtfs_rt')
    agency_option(parser)
    parser.add_argument(
        '--alerts_url',
        '-aurl',
        '-al',
        required='false',
        help="url to gtfs (or gtfs-realtime) data"
    )
    parser.add_argument(
        '--trips_url',
        '-turl',
        '-t',
        required='false',
        help="url to gtfs (or gtfs-realtime) data"
    )
    parser.add_argument(
        '--vehcles_url',
        '-vurl',
        '-v',
        required='false',
        help="url to gtfs (or gtfs-realtime) data"
    )

    return parser