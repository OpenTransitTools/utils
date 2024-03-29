import os
from re import T
import requests
import socket
import simplejson as json
import contextlib

from .compat_2_to_3 import *

import logging
log = logging.getLogger(__file__)


def rec_array_to_dict(rec_array, name_ele='name', content_ele=None):
    """
    convert an array of recs to a dictionary, ala
      [{'name': 'a', 'blah': 'blah'}, {'name': 'b', 'blah': 'blah'}]
      -to-
      {'a': {'name': 'a', 'blah': 'blah'}, 'b': {'name': 'b', 'blah': 'blah'} }
    """
    ret_val = {}
    for r in rec_array:
        if name_ele in r and r[name_ele]:
            name = r[name_ele]
            if content_ele:
                if content_ele in r:
                    ret_val[name] = r[content_ele]
            else:
                ret_val[name] = r
    return ret_val


def exists_in(rec, ele1, ele2=None, ele3=None):
    """
    check whether a (nested) element exists in a dict
    """
    ret_val = False
    if rec and ele1 and ele1 in rec:
        ret_val = True
        if ele2:
            if ele2 not in rec[ele1]:
                ret_val = False
            elif ele3 and ele3 not in rec[ele1][ele2]:
                ret_val = False
    return ret_val


def stream_json(url, args=None, extra_path=None, raw_data=False, def_val={}):
    """
    utility class to stream .json
    """
    ret_val = def_val
    try:
        if extra_path:
            url = "{0}/{1}".format(url, extra_path)
        if args:
            url = "{0}?{1}".format(url, args)

        # use requests to GET the .json content from this url
        response = requests.get(url)
        ret_val = response.text if raw_data else response.json()
        response.close()
    except Exception as e:
            ret_val = def_val
            log.error(url)
            log.error(e)
    return ret_val


def get_json(file_name, path='ott/utils/tests/json', def_val={}):
    """
    utility method to load a static .json file (usually used for testing)
    """
    ret_val = def_val

    # try one with just file_name
    jsn = file_to_json(file_name, None)

    # try two with path prepended to file name
    if jsn is None:
        p = os.path.join(path, file_name)
        jsn = file_to_json(p, None)

    # if we get valid json from either call above, that's the response
    if jsn:
        ret_val = jsn

    return ret_val


def file_to_json(file_path, def_val={}):
    """
    utility method to load a static .json file (usually used in testing)
    """
    ret_val = def_val
    try:
        with open(file_path) as f:
            ret_val = json.load(f)
    except Exception as e:
        log.info(e)

    return ret_val


def str_to_json(str, def_val={}):
    """
    utility function to load a static .json file for mock'ing a service
    """
    ret_val = def_val
    try:
        ret_val = json.loads(str)
    except Exception as e:
        log.info("Couldn't convert {0} to json\n{1}".format(str, e))
    return ret_val


def obj_to_dict(obj):
    """ Represent instance of a class as JSON object (dictionary of named elements) 
        :returns a nested dictionary that represents a JSON-encoded object.
        @from: http://stackoverflow.com/a/4682553/2125598
        NOTE: reecursively walks object's hierarchy, creating a nested dict representing the elements of the class
    """
    if obj is None:
        return None
    if isinstance(obj, (bool, int, long, float, basestring)):
        return obj
    elif isinstance(obj, dict):
        obj = obj.copy()
        for key in obj:
            obj[key.lower()] = obj_to_dict(obj[key])
        return obj
    elif isinstance(obj, list):
        return [obj_to_dict(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(obj_to_dict([item for item in obj]))
    elif hasattr(obj, '__dict__'):
        return obj_to_dict(obj.__dict__)
    else:
        return repr(obj) # Don't know how to handle, convert to string


def dict_to_json_str(data, pretty_print=False, indent=4):
    """ dump nested dict into string """
    if pretty_print:
        ret_val = json.dumps(data, sort_keys=True, indent=indent)
    else:
        ret_val = json.dumps(data)
    return ret_val


def dict_to_json_file(file_path, data, pretty_print=False, indent=4):
    with open(file_path, 'w+') as outfile:
        if pretty_print:
            json.dump(data, outfile, sort_keys=True, indent=indent)
        else:
            json.dump(data, outfile)


def object_to_json_file(file_path, obj, pretty_print=False, indent=4):
    # import pdb; pdb.set_trace()
    data = obj_to_dict(obj)
    dict_to_json_file(file_path, data, pretty_print, indent)


def json_repr(obj, pretty_print=False):
    # step 1: call serializer, which walks object tree and returns a cleaned up dict representation of the object
    data = obj_to_dict(obj)

    # step 2: dump serialized object into json string
    return dict_to_json_str(data, pretty_print)


def proxy_json(url, query_string=None, def_val={'error': 'all your stream no good'}):
    """
    will call a json url and send back response / error string...
    """
    ret_val = def_val
    try:
        ret_val = stream_json(url, query_string)
    except Exception as e:
        log.warning(e)
        ret_val['url'] = url
    return ret_val


def append_to_json(json, name, val):
    """
    simple util to add an element to json / dict
    """
    try:
        json[name] = val
    except Exception as e:
        log.warning("couldn't append '{}: {} to json data".format(name, val))


def find_element_in_json(json, name, val):
    """
    """
    try:
        json[name] = val
    except Exception as e:
        log.warning("couldn't append '{}: {} to json data".format(name, val))


def append_envvar_to_json(json, name, def_val=None):
    """
    simple util to add an element to json / dict
    """
    val = os.getenv(name, def_val)
    append_to_json(json, name.lower(), val)


def append_hostname_to_json(json):
    """
    simple util to add hostname to json file
    will look via sockets, then environs for information
    """
    name = "HOSTNAME"

    # import pdb; pdb.set_trace()
    val = socket.gethostname()
    if val is None:
        val = os.getenv(name)
    if val is None:
        val = os.getenv("COMPUTERNAME")  # Windows
    append_to_json(json, name.lower(), val)
