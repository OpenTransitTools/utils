from .base_cmdline import *


def is_spatial(parser):
    parser.add_argument(
        '--is_geospatial',
        '-geo',
        '-g',
        action="store_true",
        help="add geometry columns"
    )


def db_parser(prog_name='bin/loader', tables=['Could be (Decarative) Base.metadata.sorted_tables'], url_required=True, do_parse=False, add_misc=False):
    """
    create a generic database commandline arg PARSER
    """
    from .base_cmdline import blank_parser
    parser = blank_parser(prog_name, add_misc)

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
        '--user',
        '-user',
        '-u',
        help="database user"
    )
    parser.add_argument(
        '--tables',
        choices=tables, default=None, nargs='*',
        help="Limited list of TABLES to load, if blank, load all tables"
    )
    create_option(parser)
    clear_option(parser)
    is_spatial(parser)

    # return either parser or args
    if do_parse:
        ret_val = parser.parse_args()
    else:
        ret_val = parser
    return ret_val
