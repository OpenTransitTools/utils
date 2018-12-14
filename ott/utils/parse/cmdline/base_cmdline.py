def blank_parser(prog_name='bin/ott_blah'):
    """
    create a generic OTP commandline arg PARSER
    """
    import argparse
    parser = argparse.ArgumentParser(
        prog=prog_name,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-force", "--force",
                        help="Force update flag",
                        action="store_true"
    )
    return parser


def server_option(parser, required=False, def_val='all', help_msg="which server (maps7, svrX, etc...) should I send this to? "):
    parser.add_argument(
        '--server',
        '-svr',
        '-s',
        required=required,
        default=def_val,
        help=help_msg
    )


def misc_option(parser, required=False, limit=111):
    parser.add_argument(
        '--limit',
        '-lim',
        '-l',
        required=required,
        default=limit,
        help="limit results"
    )
