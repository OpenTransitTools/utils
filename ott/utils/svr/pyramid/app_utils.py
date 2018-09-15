

def add_cors_headers_response_callback(event):
    """
    add CORS so the requests can work from different (test / development) port
    do this at least for testing ... might not make call in production
    :param event:

    :see config.add_subscriber(add_cors_headers_response_callback, NewRequest):

    :see credit goes to https://stackoverflow.com/users/211490/wichert-akkerman
    :see https://stackoverflow.com/questions/21107057/pyramid-cors-for-ajax-requests
    """
    def cors_headers(request, response):
        response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
            'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, Authorization',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Max-Age': '1728000',
        })

    # set the function above to be called for each response, where we'll set the CORS headers
    event.request.add_response_callback(cors_headers)
