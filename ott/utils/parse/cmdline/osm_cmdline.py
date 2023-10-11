from .base_cmdline import blank_parser


def osm_parser(prog_name='bin/osm_process', do_parse=False, **kwargs):
    """ create a generic OSM processor commandline arg PARSER """
    parser = blank_parser(prog_name)
    parser.add_argument(
        '--pbf',
        '-pbf',
        '-p',
        required=False,
        help=".pbf url or file path"
    )
    parser.add_argument(
        '--osm',
        '-osm',
        '-o',
        required=kwargs.get('osm_required'),
        help=".osm url or file path"
    )
    parser.add_argument(
        '--output',
        '-out',
        required=kwargs.get('out_required'),
        help=".osm (or .pbf) file name / path to write osm output"
    )
    parser.add_argument(
        '--osmosis_exe',
        '--exe',
        '-e',
        required=kwargs.get('exe_required'),
        help="path to OSMOSIS binary"
    )
    ret_val = parser
    if do_parse:
        ret_val = parser.parse_args()
    return ret_val


def osm_parser_args(prog_name, **kwargs):
    return osm_parser(prog_name, True, **kwargs)


def geoserver_parser(prog_name='bin/generate_geoserver_config', do_parse=True):
    """ create a generic GEOSERVER processor commandline arg PARSER """

    # TODO: think about moving some of this to db_cmdline

    # default values
    def_dir = "data_dir"
    workspace = "ott"
    db_url = "localhost"
    db_port = "5432"

    parser = blank_parser(prog_name)
    parser.add_argument(
        '--data_dir',
        '-data_dir',
        '-dd',
        required=False,
        default=def_dir,
        help="path to geoserver 'data' directory"
    )
    parser.add_argument(
        '--workspace',
        '-workspace',
        '-ws',
        required=False,
        default=workspace,
        help="path to geoserver 'data' directory"
    )
    parser.add_argument(
        '--db_url',
        '-db_url',
        '-db',
        '-url',
        required=False,
        default=db_url,
        help="db url (localhost or docker url, ala 'db')"
    )
    parser.add_argument(
        '--db_port',
        '-db_port',
        '-port',
        required=False,
        default=db_port,
        help="db port (5432 is the default pg port)"
    )

    ret_val = parser
    if do_parse:
        ret_val = parser.parse_args()
    return ret_val
