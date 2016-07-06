import sys
import string
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

def camel_to_underscore(name):
    '''convert a camel case string to snake case'''
    for char in string.ascii_uppercase:
        name = name.replace(char, '_{0}'.format(char))
    return name.lower()

def underscore_to_camel(name):
    '''convert a snake case string to camel case'''
    string_list = name.strip('_').split('_')
    result = string_list[0].lower()
    for s in string_list[1:]:
        result = '{0}{1}'.format(result, s.title())
    return result
