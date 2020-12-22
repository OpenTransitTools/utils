import os
import string
import logging
log = logging.getLogger(__file__)


def get_val(val, def_val=None):
    ret_val = def_val
    if val and len(val) > 0:
        ret_val = val
    if ret_val == 'None' or ret_val == 'null':
        ret_val = None
    return ret_val


def safe_index(val, search):
    ret_val = -1
    try:
        ret_val = val.index(search)
    except ValueError:
        ret_val = -1
    return ret_val


def safe_replace(val, target="", replace=""):
    ret_val = val
    try:
        if len(target) > 0:
            ret_val = val.replace(target, replace)
    except:
        pass
    return ret_val


def safe_append(str1, str2, def_val=None):
    ret_val = def_val
    try:
        ret_val = str1 + str2
    except Exception as e:
        log.debug(e)
        if ret_val is None and (str1 or str2):
            ret_val = str1 if str1 else str2
    return ret_val


def safe_path_join(str1, str2, def_val=None):
    ret_val = def_val
    try:
        ret_val = os.path.join(str1, str2)
    except Exception as e:
        log.debug(e)
    return ret_val


def is_in_string(in_str, targets):
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
    """ convert a camel case string to snake case
    """
    for char in string.ascii_uppercase:
        name = name.replace(char, '_{0}'.format(char))
    return name.lower()


def underscore_to_camel(name):
    """convert a snake case string to camel case"""
    string_list = name.strip('_').split('_')
    result = string_list[0].lower()
    for s in string_list[1:]:
        result = '{0}{1}'.format(result, s.title())
    return result
