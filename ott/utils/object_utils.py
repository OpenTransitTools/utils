import sys
import base64
import hashlib
from .compat_2_to_3 import *
import logging
log = logging.getLogger(__file__)


class SimpleObject(object):
    pass


def to_hash(str):
    """ generates nice 0AI3Mk6FErSH4Q== type hashes from strings """
    hasher = hashlib.sha1(str)
    ret_val = base64.urlsafe_b64encode(hasher.digest()[0:10])
    return ret_val


def get_error_message(err, def_val=None):
    """ return error message from an OTP error object
        {'error': {'msg': 'Origin is within a trivial distance of the destination.', 'id': 409}}
    """
    ret_val = def_val
    try:
        ret_val = err.error.msg
    except:
        try:
            ret_val = err['error']['msg']
        except:
            try:
                if err['has_errors'] and err['status_message']:
                    ret_val = err['status_message']
            except:
                ret_val = def_val
    return ret_val


def update_object(tgt, src):
    """ copy values from src to tgt, for any shared element names between the two objects
    """
    for k, v in src.__dict__.items():
        try:
            if tgt.__dict__.has_key(k):
                tgt.__dict__[k] = v
        except:
            pass


def get_striped_dict_val(dict, name, def_val=None, strip_all_spaces=False, warn_not_avail=True):
    """ grab a value from a dict, which strips spaces (and potentially all spaces)
    """
    ret_val = def_val
    try:
        if name in dict:
            p = dict[name]
            if p and len(p) > 0:
                ret_val = p.strip()
                if strip_all_spaces:
                    ret_val = ret_val.replace(' ', '')
        elif warn_not_avail:
            log.warning("'{0}' was not found as an index in record {1}".format(name, dict))
    except:
        log.warning("'{0}' was not found as an index in record {1}".format(name, dict))
    return ret_val


def str_compare(str1, str2, insensitive=True):
    ret_val = False
    try:
        if insensitive: 
            if str1.lower() == str2.lower():
                ret_val = True
        else:
            if str1 == str2:
                ret_val = True
    except:
        pass
    return ret_val


def fix_url(url):
    """ do things like escape the & in intersection names, ala "17th %26 Center"
    """
    ret_val = url
    ret_val = ret_val.replace(" & ", " %26 ")
    return ret_val


def is_match(param_val, match_val, none_is_match=True, all_is_match=True, def_val=False):
    ret_val = def_val
    try:
        if param_val:
            if param_val.lower() == 'all':
                ret_val = all_is_match
            elif param_val in match_val:
                ret_val = True
        else:
            ret_val = none_is_match
    except:
        ret_val = def_val
    return ret_val


def is_not_match(param_val, match_val, none_is_match=True, all_is_match=True, def_val=False):
    return not is_match(param_val, match_val, none_is_match, all_is_match, def_val)


def has_content(obj):
    ret_val = False
    if obj:
        ret_val = True
        if isinstance(obj, basestring) and len(obj) <= 0:
            ret_val = False
    return ret_val


def is_list(obj, key):
    ret_val = False
    try:
        ret_val = isinstance(obj[key], list)
    except:
        pass
    return ret_val


def safe_dict_val(obj, key, def_val=None):
    ret_val = def_val
    try:
        ret_val = obj[key]
    except:
        pass
    return ret_val


def safe_array_val(list, index, def_val=None):
    ret_val = def_val
    try:
        ret_val = list[index]
    except:
        pass
    return ret_val


def safe_str(obj, def_val=''):
    ret_val = def_val
    try:
        ret_val = str(obj)
    except:
        pass
    return ret_val


def safe_int(obj, def_val=0):
    ret_val = def_val
    try:
        ret_val = int(obj)
    except:
        pass
    return ret_val


def safe_float(obj, def_val=0.0):
    ret_val = def_val
    try:
        ret_val = float(obj)
    except:
        pass
    return ret_val


def safe_get(obj, key, def_val=None):
    """ try to return the key'd value from either a class or a dict
        (or return the raw value if we were handed a native type)
    """
    ret_val = def_val
    try:
        ret_val = getattr(obj, key)
    except:
        try:
            ret_val = obj[key]
        except:
            if isinstance(obj, (float, int, str)):
                ret_val = obj
    return ret_val


def safe_get_str(obj, key, def_val=''):
    return safe_str(safe_get(obj, key), def_val)


def safe_get_int(obj, key, def_val=0):
    return safe_int(safe_get(obj, key), def_val)


def safe_get_float(obj, key, def_val=0.0):
    return safe_float(safe_get(obj, key), def_val)


def safe_get_any(obj, keys, def_val=None):
    """ :return object element value matching the first key to have an associated value
    """
    ret_val = def_val
    for k in keys:
        v = safe_get(obj, k)
        if v and len(v) > 0:
            ret_val = v
            break
    return ret_val


def safe_set_from_dict(obj, key, src={}, always_cpy=True, def_val=None):
    """
    will set an object's attribute from a value in a source dict
    """

    # step 1: handle def_val
    try:
        if def_val is None and hasattr(obj, key):
            def_val = getattr(obj, key)
    except Exception as e:
        log.info(e)

    # step 2: copy values from dict to object attribute
    try:
        if always_cpy or key in src:
            val = src.get(key, def_val)
            if val or always_cpy:
                setattr(obj, key, val)
    except Exception as e:
        log.info(e)


def list_to_str(list, sep=" "):
    ret_val = ""
    try:
        for n in list:
            ret_val += n + sep
        ret_val = ret_val.rstrip(sep)
    except:
        ret_val = to_str(list)
    return ret_val


def str_to_list(str, def_val=[]):
    """
    try to return a list of some sort
    """
    ret_val = def_val
    try:
        ret_val = str.split(",")
    finally:
        try:
            if ret_val is None:
                ret_val = [str]
        except:
            pass
    return ret_val


def list_val(list, index=0, def_val=None):
    ret_val = def_val
    try:
        ret_val = list[index]
    except Exception as e:
        log.info(e)
    return ret_val


def dval(obj, key, def_val=None):
    return safe_dict_val(obj, key, def_val)


def dval_list(obj, key, def_val=[]):
    return safe_dict_val(obj, key, def_val)


def strip_tuple(obj, def_val=None):
    ret_val = def_val
    try:
        ret_val = obj[0]
    except:
        pass
    return ret_val


def strip_tuple_list(obj_list, def_val=None):
    ret_val = def_val
    try:
        rv = []
        for o in obj_list:
            z = strip_tuple(o)
            rv.append(z)
        ret_val = rv
    except:
        pass
    return ret_val


def to_str(s, def_val=''):
    """
    multi-byte compliant version of str() unicode conversion...
    """
    ret_val = def_val
    try:
        ret_val = str(s)
    except:
        try:
            ret_val = s.encode('utf-8')
        except:
            pass
    return ret_val


def to_url_param_val(s, def_val=''):
    ret_val = to_str(s, def_val)
    try:
        ret_val = ret_val.strip()
        ret_val = ret_val.replace(' ', '+').replace('&amp;', '%26').replace('&', '%26')
    except:
        pass
    return ret_val


def to_code(s, def_val=''):
    """ multi-byte compliant version of str() unicode conversion...
    """
    ret_val = def_val
    try:
        ret_val = decode(s, 'utf-8')
    except:
        try:
            ret_val = str(s)
        except:
            pass
    return ret_val


def to_str_code(s, def_val=''):
    """ multi-byte compliant version of str() unicode conversion...
    """
    ret_val = def_val
    try:
        ret_val = decode(s, 'utf-8')
    except:
        try:
            ret_val = str(s)
        except:
            pass
    return ret_val


def dict_update(src, target, append=False):
    """ better than the dict.update(), in that None or '' won't overwrite values
        @param: append variable will append new source into target (regardless of value)
        @return: nothing ... will update / append values to 'target' parameter
    """
    for k,v in src.iteritems():
        if k in target:
            if v:
                target[k] = v
        elif append:
            target[k] = v


def is_force_update(argv=sys.argv, force=["force", "update", "reload"]):
    """ scan argv for words that indicate an update is necessary
    """
    ret_val = False

    # test 1 : force update word is a url parameter
    for f in force:
        if f in argv:
            ret_val = True
            break;

    # test 2 : force update word sub-string in  url parameter
    if ret_val is False:
        first = True
        for a in argv:
            # skip app path at argv[0]
            if first:
                first = False
                continue
            for f in force:
                if f in a:
                    ret_val = True
                    break
    return ret_val


def find_elements(key, obj):
    """
    find elements of dict (e.g. json) object via the key
    note: could be better with generators maybe, but 3.7 kinda f's up generators (StopIteration), so I don't have time
    note: this isn't perfect (by any means), since json can start with an top-level array I guess...
    """
    ret_val = []

    # import pdb; pdb.set_trace()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                ret_val.append(v)
            elif isinstance(v, dict):
                n = find_elements(key, v)
                if n and len(n) > 0:
                    ret_val = ret_val + n
            elif isinstance(v, list):
                for d in v:
                    n = find_elements(key, d)
                    if n and len(n) > 0:
                        ret_val = ret_val + n

    return ret_val

