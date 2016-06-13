import re
import logging
log = logging.getLogger(__file__)

def contains(regexp, str):
    ''' does string have one or more instances of regexp
    '''
    ret_val = False
    try:
        a = re.findall(regexp, str.strip())
        if a and len(a) > 0:
            ret_val = True
    except:
        pass
    return ret_val
