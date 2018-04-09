import logging
log = logging.getLogger(__file__)


def osm_parser(prog_name='bin/osm_process'):
    """ create a generic database commandline arg PARSER """
    import argparse
    parser = argparse.ArgumentParser(
        prog=prog_name,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--osm',
        '-o',
        required=False,
        help=".osm url or file path"
    )
    parser.add_argument(
        '--pbf',
        '-p',
        required=False,
        help=".pbf url or file path"
    )
    return parser


def osm_parser_args(prog_name):
    parser = osm_parser(prog_name)
    return parser.parse_args()