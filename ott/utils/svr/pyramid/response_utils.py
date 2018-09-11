from ott.utils import json_utils
from .globals import *

import logging
log = logging.getLogger(__file__)


def dao_response(dao):
    """ using a BaseDao object, send the data to a pyramid Reponse """
    if dao is None:
        dao = DATA_NOT_FOUND_MSG
    return json_response(json_data=dao.to_json(), status=dao.status_code)


def json_response_list(lst, mime='application/json', status=200):
    """ @return Response() with content_type of 'application/json' """
    json_data = []
    for l in lst:
        if l:
            jd = l.to_json()
            json_data.append(jd)
    return json_response(json_data, mime, status)


def json_response(json_data, mime='application/json', status=200):
    """ @return Response() with content_type of 'application/json' """
    from pyramid.response import Response

    if json_data is None:
        json_data = DATA_NOT_FOUND_MSG.to_json()
    return Response(json_data, content_type=mime, status_int=status)


def proxy_json(url, query_string):
    """
    will call a json url and send back response / error string...
    """
    ret_val = None
    try:
        ret_val = json_utils.stream_json(url, query_string)
    except Exception as e:
        log.warning(e)
        ret_val = SYSTEM_ERR_MSG.status_message
    finally:
        pass
    return ret_val


def sys_error_response():
    return dao_response(SYSTEM_ERROR_MSG)


def data_not_found_response():
    return dao_response(DATA_NOT_FOUND_MSG)
