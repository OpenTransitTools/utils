import logging
log = logging.getLogger(__file__)


def blank_parser(prog_name='bin/otp_process'):
    """
    create a generic OTP commandline arg PARSER
    """
    import argparse
    parser = argparse.ArgumentParser(
        prog=prog_name,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    return parser


def base_parser(prog_name='bin/otp_process'):
    parser = blank_parser(prog_name)
    parser.add_argument('name', default="all", nargs='?',
                        help="Name of OTP graph folder in the 'cache' build (e.g., 'all', 'prod', 'test' or 'call')")
    return parser


def test_option(parser, required=False, def_val='all', help_msg="regex name of test suites to run (e.g., 'rail', 'bus|rail', etc...)"):
    parser.add_argument(
        '--test_suite',
        '-ts',
        required=required,
        help=help_msg
    )


def server_option(parser, required=False, def_val='all', help_msg="which server (maps7, svrX, etc...) should I send this to? "):
    parser.add_argument(
        '--server',
        '-svr',
        '-s',
        default=def_val,
        help=help_msg
    )
