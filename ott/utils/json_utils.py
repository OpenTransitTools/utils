# FXP TODO -- commenting this out, since it might be f'n with performance
#import socket
#socket.setdefaulttimeout(40)
import os
import logging
log = logging.getLogger(__file__)

import simplejson as json
import urllib
import contextlib


def stream_json(u, args=None, extra_path=None):
    """ utility class to stream .json
    """
    ret_val={}
    url = u
    if extra_path:
        url = "{0}/{1}".format(url, extra_path)
    if args:
        url = "{0}?{1}".format(url, args)
    with contextlib.closing(urllib.urlopen(url)) as stream:
        otp = stream.read()
        ret_val = json.loads(otp)
    return ret_val


def get_json(file, path='ott/utils/tests/json'):
    """ utility class to load a static .json file for mock'ing a service
    """
    ret_val={}
    try:
        with open(file) as f:
            ret_val = json.load(f)
    except:
        try:
            path=os.path.join(path, file)
            with open(path) as f:
                ret_val = json.load(f)
        except:
            log.info("Couldn't open file : {0} (or {1})".format(file, path))

    return ret_val


def str_to_json(str, def_val={}):
    """ utility class to load a static .json file for mock'ing a service
    """
    ret_val=def_val
    try:
        ret_val = json.loads(str)
    except Exception, e:
        log.info("Couldn't convert {0} to json\n{1}".format(str, e))

    return ret_val


def serialize(obj):
    """ Represent instance of a class as JSON.
        returns a string that represents a JSON-encoded object.
        @from: http://stackoverflow.com/a/4682553/2125598

        Recursively walk object's hierarchy.
    """
    if(obj is None):
        return None
    if isinstance(obj, (bool, int, long, float, basestring)):
        return obj
    elif isinstance(obj, dict):
        obj = obj.copy()
        for key in obj:
            obj[key.lower()] = serialize(obj[key])
        return obj
    elif isinstance(obj, list):
        return [serialize(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(serialize([item for item in obj]))
    elif hasattr(obj, '__dict__'):
        return serialize(obj.__dict__)
    else:
        return repr(obj) # Don't know how to handle, convert to string


def json_repr(obj, pretty_print=False):

    ## step 1: call serializer, which walks object tree and returns a cleaned up dict representation of the object
    data = serialize(obj)

    ## step 2: dump serialized object into json string
    ret_val = None
    if pretty_print:
        ret_val = json.dumps(data, sort_keys=True, indent=4)
    else:
        ret_val = json.dumps(data)

    ## step 3: return result as string
    return ret_val


def object_to_json_file(file_path, obj, pretty_print=False):
    data = serialize(obj)
    with open(file_path, 'w') as outfile:
        if pretty_print:
            json.dump(data, outfile, sort_keys=True, indent=4)
        else:
            json.dump(data, outfile)
