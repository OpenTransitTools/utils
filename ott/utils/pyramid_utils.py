import logging
log = logging.getLogger(__file__)


def url_response(host, service, id, agency_id=None, extra="&detailed"):
    """ return a url with id and other good stuff
    """
    url = "http://{}/{}?id={}"
    if agency_id:
        url = url + "&agency_id={}".format(agency_id)
    if extra:
        url = url + extra
    ret_val = url.format(host, service, id)
    return ret_val


def dao_response(dao):
    """ using a BaseDao object, send the data to a pyramid Reponse """
    if dao is None:
        dao = data_not_found
    return json_response(json_data=dao.to_json(), status=dao.status_code)


def json_response(json_data, mime='application/json', status=200):
    """ @return Response() with content_type of 'application/json' """
    if json_data is None:
        json_data = data_not_found.to_json()
    return Response(json_data, content_type=mime, status_int=status)


def json_response_list(lst, mime='application/json', status=200):
    """ @return Response() with content_type of 'application/json' """
    json_data = []
    for l in lst:
        if l:
            jd = l.to_json()
            json_data.append(jd)
    return json_response(json_data, mime, status)


def proxy_json(url, query_string):
    """ will call a json url and send back response / error string...
    """
    ret_val = None
    try:
        ret_val = json_utils.stream_json(url, query_string)
    except Exception as e:
        log.warning(e)
        ret_val = system_err_msg.status_message
    finally:
        pass

    return ret_val

