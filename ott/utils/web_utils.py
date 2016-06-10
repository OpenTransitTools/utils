import os
import socket
import urllib2
import wget as wget_wget
import logging
log = logging.getLogger(__file__)


def email(frm, to, msg, subject="loader email"):
    log.info("email: TODO...implement me")

def get_hostname():
    return socket.gethostname()

def my_wget(url, file_name):
    """ wget a file from url
        IMPORTANT NOTE: this will *not* work if the URL is a redirect, etc...
    """
    is_success = True
    try:
        # get gtfs file from url
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)

        # write it out
        f = open(file_name, 'wb')
        f.write(res.read())
        f.flush()
        f.close()
        res.close()

        log.info("wget: downloaded {} into file {}".format(url, file_name))
    except Exception, e:
        log.warn(e)
        is_success = False

def wget(url, file_name):
    """ wget a file from url
        IMPORTANT NOTE: this will *not* work if the URL is a redirect, etc...
    """
    is_success = True
    wget_wget.download(url, file_name)
    log.info("wget: downloaded {} into file {}".format(url, file_name))
    return is_success
