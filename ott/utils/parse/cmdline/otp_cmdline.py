from .base_cmdline import *


def base_parser(prog_name='bin/otp_process'):
    parser = blank_parser(prog_name)
    parser.add_argument('name', default="all", nargs='?',
                        help="Name of OTP graph folder in the 'cache' build (e.g., 'all', 'prod', 'test' or 'call')")
    return parser


def test_option(parser, required=False, def_val='bus|rail', help_msg="regex name of test suites to run (e.g., 'rail', 'bus|rail', etc...)"):
    parser.add_argument(
        '--test_suite',
        '-ts',
        required=required,
        default=def_val,
        help=help_msg
    )
