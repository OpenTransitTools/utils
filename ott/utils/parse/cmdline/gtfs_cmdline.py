from .base_cmdline import *


def agency_option(parser, required=False, def_val='all', help_msg="GTFS agency id (i.e., might also be a db schema name)"):
    parser.add_argument(
        '--agency_id',
        '-agency',
        '-a',
        required=required,
        default=def_val,
        help=help_msg
    )


def url_option(parser, required=True, help_msg="url to gtfs feed (ala https://developers.google.com/transit/gtfs/examples/sample-feed.zip)"):
    parser.add_argument(
        '--url',
        '-url',
        '-u',
        required=required,
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


def api_key(parser, required=False, help_msg="api key needed to access this data"):
    parser.add_argument(
        '--api_key',
        '-akey',
        '-ak',
        required=required,
        help=help_msg
    )


def simple_stop_route_parser(parser=None, do_parse=True):
    """ simple stop & route cmd line parser """
    if parser is None:
        parser = blank_parser('bin/stop_route')
    agency_option(parser)
    stop_option(parser)
    route_option(parser)
    misc_option(parser)
    ret_val = parser
    if do_parse:
        # finalize the parser
        ret_val = parser.parse_args()
    return ret_val


def gtfs_parser(exe_name='bin/gtfs', do_parse=True):
    """ simple select agency PARSER """
    parser = blank_parser(exe_name)
    agency_option(parser)
    ret_val = parser
    if do_parse:
        # finalize the parser
        ret_val = parser.parse_args()
    return ret_val


def gtfs_download_parser(exe_name='bin/download_gtfs', do_parse=True):
    """ create a commandline arg PARSER for downloading gtfs files """
    parser = blank_parser(exe_name)
    agency_option(parser, True)
    url_option(parser, True)
    ret_val = parser
    if do_parse:
        # finalize the parser
        ret_val = parser.parse_args()
    return ret_val


def gtfs_rt_parser(api_key_required=False, api_key_msg=None, exe_name='bin/load_gtfs_rt', do_parse=True):
    """ create a database and gtfs rt commandline arg PARSER """
    from . import db_cmdline
    parser = db_cmdline.db_parser(exe_name)
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

    ret_val = parser
    if do_parse:
        # finalize the parser
        ret_val = parser.parse_args()
    return ret_val
