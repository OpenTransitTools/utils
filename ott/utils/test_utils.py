""" Log utils ... routines to help testing
"""



def loop_urls(url_file, match=None, batch_size=5, pause=None):
    """ run thru URLs, calling those urls in parallel batch sizes (stress and speed of processing)
    """
    t = m = f = 0
    batch = []

    import web_utils
    def process_batch():
        """ process batch of urls
            TODO threads .... how to make multiple calls in parallel???
        """
        for url in batch:
            s, r = web_utils.get(url)
            t += 1
            if not s:
                f += 1
            if match:
                if match in r:
                    m += 1
            else:
                m += 1

    with open(url_file) as file:
        k = 0
        for u in file:
            batch.append(u)
            k += 1
            if k == batch_size:
                k = 0
                process_batch
                del batch[:]  # clear batch list

    ret_val = {'total': t, 'match': m, 'failed_connect': f}
    return ret_val
