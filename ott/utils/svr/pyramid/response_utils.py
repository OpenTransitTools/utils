from ott.utils.dao.base import DatabaseNotFound
from ott.utils.dao.base import ServerError


import logging
log = logging.getLogger(__file__)

# only need to create these classes once...
data_not_found_msg = DatabaseNotFound()
system_error_msg = ServerError()


def dao_response(dao):
    """ using a BaseDao object, send the data to a pyramid Reponse """
    if dao is None:
        dao = data_not_found
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
        json_data = data_not_found.to_json()
    return Response(json_data, content_type=mime, status_int=status)


def sys_error_response():
    return dao_response(system_error_msg)


def data_not_found_response():
    return dao_response(data_not_found_msg)