def db_parser(prog_name='bin/loader', tables=['Could be (Decarative) Base.metadata.sorted_tables'], url_required=True, do_parse=False, add_misc=False):
    """
    create a generic database commandline arg PARSER
    """
    import argparse
    parser = argparse.ArgumentParser(
        prog=prog_name,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--database_url',
        '-d',
        required=url_required,
        help="(geo) database url ala dialect+driver://user:password@host/dbname[?key=value..]"
    )
    parser.add_argument(
        '--schema',
        '-schema',
        '-s',
        help="database schema"
    )
    parser.add_argument(
        '--tables',
        choices=tables, default=None, nargs='*',
        help="Limited list of TABLES to load, if blank, load all tables"
    )
    create_and_clear(parser)
    is_spatial(parser)
    if add_misc:
        from .base_cmdline import misc_option
        misc_option(parser)

    # return either parser or args
    if do_parse:
        ret_val = parser.parse_args()
    else:
        ret_val = parser
    return ret_val


def create_and_clear(parser):
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
        '-cl',
        action="store_true",
        help="clear table(s) before loading"
    )


def is_spatial(parser):
    parser.add_argument(
        '--is_geospatial',
        '-geo',
        '-g',
        action="store_true",
        help="add geometry columns"
    )
