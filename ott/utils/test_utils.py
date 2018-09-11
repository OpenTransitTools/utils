""" Log utils ... routines to help testing
"""


def loop_urls(url_file, match=None, batch_size=5, pause=None):
    """ run thru URLs, calling those urls in parallel batch sizes (stress and speed of processing)
    """
    t = m = f = 0

    from . import web_utils

    def process_batch(url, t, m, f):
        """ process batch of urls
            TODO threads .... how to make multiple calls in parallel???
        """
        # import pdb; pdb.set_trace()
        s, r = web_utils.get(url)
        t += 1
        if not s:
            f += 1
        if match:
            if match in r:
                m += 1
        else:
            m += 1
        return t, m, f

    with open(url_file) as file:
        k = 0
        batch = []
        for u in file:
            batch.append(u)
            k += 1
            if k == batch_size:
                k = 0
                for url in batch:
                    t, m, f = process_batch(url, t, m, f)
                del batch[:]  # clear batch list

    ret_val = {'total': t, 'match': m, 'failed_connect': f}
    return ret_val
