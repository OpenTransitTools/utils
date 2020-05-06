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


def geoserver_parser(prog_name='bin/generate_geoserver_config', do_parse=True, def_dir="geoserver/data"):
    """ create a generic GEOSERVER processor commandline arg PARSER """
    parser = blank_parser(prog_name)
    parser.add_argument(
        '--ignore_layergroups',
        '-il',
        action="store_true",
        help="should geoserver scripts generate layergroups configs"
    )
    parser.add_argument(
        '--data_dir',
        '-data_dir',
        '-dd',
        required=False,
        default=def_dir,
        help="path to geoserver 'data' directory"
    )

    ret_val = parser
    if do_parse:
        ret_val = parser.parse_args()
    return ret_val

