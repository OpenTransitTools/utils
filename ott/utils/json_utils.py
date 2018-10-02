import os
import simplejson as json
import contextlib

from future.standard_library import install_aliases; install_aliases() # for py 2 and 3 compat w/urllib
import urllib

import logging
log = logging.getLogger(__file__)


def stream_json(url, args=None, extra_path=None, def_val={}):
    """
    utility class to stream .json
    """
    ret_val = def_val
    if extra_path:
        url = "{0}/{1}".format(url, extra_path)
    if args:
        url = "{0}?{1}".format(url, args)
    with contextlib.closing(urllib.request.urlopen(url)) as stream:
        content_string = stream.read().decode('utf-8')
        ret_val = json.loads(content_string)
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


def dict_to_json_str(data, pretty_print=False):
    """ dump nested dict into string """
    ret_val = None
    if pretty_print:
        ret_val = json.dumps(data, sort_keys=True, indent=4)
    else:
        ret_val = json.dumps(data)
    return ret_val


def object_to_json_file(file_path, obj, pretty_print=False):
    #import pdb; pdb.set_trace()
    data = obj_to_dict(obj)
    with open(file_path, 'w+') as outfile:
        if pretty_print:
            json.dump(data, outfile, sort_keys=True, indent=4)
        else:
            json.dump(data, outfile)


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
    return ret_val
