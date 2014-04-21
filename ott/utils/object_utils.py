import datetime
import simplejson as json
import logging
log = logging.getLogger(__file__)

def get_error_message(err, def_val=None):
    ''' return error message from an OTP error object
        {'error': {'msg': 'Origin is within a trivial distance of the destination.', 'id': 409}}
    '''
    ret_val = def_val
    try:
        ret_val = err.error.msg
    except:
        ret_val = def_val
    return ret_val

def update_object(tgt, src):
    ''' copy values from src to tgt, for any shared element names between the two objects
    '''
    for k, v in src.__dict__.items():
        try:
            if tgt.__dict__.has_key(k):
                tgt.__dict__[k] = v
        except:
            pass


def fix_url(url):
    ''' do things like escape the & in intersection names, ala "17th %26 Center"
    '''
    ret_val = url
    ret_val = ret_val.replace(" & ", " %26 ")
    return ret_val


def has_content(obj):
    ret_val = False
    if obj:
        ret_val = True
        if isinstance(obj, basestring) and len(obj) <= 0:
            ret_val = False
    return ret_val


def safe_str(obj, def_val=''):
    ret_val = def_val
    try:
        ret_val = str(obj)
    except:
        pass
    return ret_val

def safe_int(obj, def_val=None):
    ret_val = def_val
    try:
        ret_val = int(obj)
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
    ''' multi-byte compliant version of str() unicode conversion...
    '''
    ret_val = def_val
    try:
        ret_val = s.encode('utf-8')
    except:
        try:
            ret_val = str(s)
        except:
            pass
    return ret_val

def to_code(s, def_val=''):
    ''' multi-byte compliant version of str() unicode conversion...
    '''
    ret_val = def_val
    try:
        ret_val = s.decode('utf-8')
    except:
        try:
            ret_val = str(s)
        except:
            pass
    return ret_val

def to_str_code(s, def_val=''):
    ''' multi-byte compliant version of str() unicode conversion...
    '''
    ret_val = def_val
    try:
        ret_val = s.decode('utf-8')
    except:
        try:
            ret_val = str(s)
        except:
            pass
    return ret_val
