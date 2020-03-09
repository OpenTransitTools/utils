
# py 3 removes basestring and long
try:
    basestring = basestring
except:
    basestring = str
try:
    long = long
except:
    long = int


import sys
from future.standard_library import install_aliases
install_aliases()  # for py 2 and 3 compat w/urllib


import urllib
try:
    import urlparse
    from urlparse import urlsplit
except:
    import urllib.request
    from urllib.parse import urlparse
    from urllib.parse import urlsplit


def decode(val, enc='utf-8'):
    if sys.version_info > (3, 0):
        bval = bytes(val, enc)
        ret_val = bval.decode(enc, 'ignore')
    else:
        ret_val = val.decode(enc)
    return ret_val