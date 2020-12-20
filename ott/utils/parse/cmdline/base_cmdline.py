def empty_parser(prog_name='bin/ott_blah'):
    """
    create a generic OTP commandline arg PARSER
    """
    import argparse
    parser = argparse.ArgumentParser(
        prog=prog_name,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    return parser


def blank_parser(prog_name, add_misc=False):
    """
    create a generic OTP commandline arg PARSER
    """
    parser = empty_parser(prog_name)
    parser.add_argument("-force", "--force",
                        help="Force update flag",
                        action="store_true"
    )
    if add_misc:
        misc_option(parser)

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


def create_option(parser, help_msg="drop / create database tables for "):
    parser.add_argument(
        '--create',
        '-create',
        '-c',
        action="store_true",
        help=help_msg
    )


def clear_option(parser, help_msg="clear things before loading/exporting"):
    parser.add_argument(
        '--clear',
        '-clear',
        '-cl',
        action="store_true",
        help=help_msg
    )


def limit_option(parser, required=False, def_val=None):
    parser.add_argument(
        '--limit',
        '-lim',
        '-l',
        required=required,
        default=def_val,
        help="limit (number): --limit 5 could mean to trim a longer list of results to just 5"
    )

def durr_option(parser, required=False, def_val=None):
    parser.add_argument(
        '--durr',
        '--duration',
        '-durr',
        required=required,
        default=def_val,
        help="duration (number): --durr 60 could be used to mean run a process for 60 seconds"
    )


def freq_option(parser, required=False, def_val=None):
    parser.add_argument(
        '--freq',
        '--frequency',
        '-freq',
        required=required,
        default=def_val,
        help="freq (number): --freq 5 could mean to run a process every 5 seconds"
    )


def misc_option(parser, required=False, limit=111, durr=False, freq=False):
    limit_option(parser, required, limit)
    durr_option(parser, required, durr)
    freq_option(parser, required, freq)
