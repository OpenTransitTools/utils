import logging
log = logging.getLogger(__file__)


def db_args():
    """ create a generic database commandline arg PARSER """
    import argparse
    parser = argparse.ArgumentParser(prog='gtfs data loader', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--database_url', '-d',  default='sqlite:///gtfs.db', help='DATABASE URL with appropriate privileges')
    parser.add_argument('--is_geospatial', '-g', default=False, action='store_true', help='Database supports GEOSPATIAL functions')
    parser.add_argument('--schema','-s', default=None, help='Database SCHEMA name')
    parser.add_argument('--gtfs','-u', default="DATAd", help='URL or local path to GTFS(RT) data')
    return parser


def dbdb_parser():
    """ create a generic database commandline arg PARSER """
    import argparse
    parser = argparse.ArgumentParser(
        prog='controller',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--agency',
        '-agency',
        '-a',
        default="trimet",
        help="agency name (string)"
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

    parser.add_argument(
        '--url',
        '-url',
        '-u',
        required='true',
        help="url to gtfs-realtime data"
    )

    args = parser.parse_args()
    return args


def db_args_gtfsdb():
    parser = db_args()
    args = parser.parse_args()
    kwargs = dict(
        url=args.database_url,
        is_geospatial=args.is_geospatial,
        schema=args.schema
    )
    return gtfsdb_conn(kwargs)


def db_gtfs_rt():
    """
    get a command line PARSER and db connection to query gtfsrdb data
    :requires ott.data project:
    NOTE: meant as a quick dirty way to grab a connection for test apps
    """
    parser = db_args()
    parser.add_argument('--route',  '-r', default="12", help='what route?')
    parser.add_argument('--agency', '-a', default="TriMet", help='what agency?')
    args = parser.parse_args()

    from ott.data.gtfsrdb import model
    model.add_schema(args.schema)
    session, engine = db_conn(args.database_url)
    return session, engine
