import logging
log = logging.getLogger(__file__)

TOKEN_FILE = ".token"


def get_cached_token(token_file=TOKEN_FILE):
    ret_val = None
    try:
        with open(token_file, 'r') as f:
            ret_val = f.read()
    except Exception as e:
        log.info(e)
    return ret_val


def put_cached_token(token, token_file=TOKEN_FILE):
    try:
        with open(token_file, 'w') as f:
            f.write(str(token))
            f.flush()
            f.close()
    except Exception as e:
        log.info(e)
