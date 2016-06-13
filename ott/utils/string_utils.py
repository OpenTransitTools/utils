import sys
import logging
log = logging.getLogger(__file__)


def is_in_string(in_str, targets):
    ''' xxx
    '''
    ret_val = False

    if targets:
        tlist = targets
        if isinstance(targets, str):
            tlist = targets.split(',')

        for t in tlist:
            if t.strip() in in_str:
                ret_val = True
                break

    return ret_val
