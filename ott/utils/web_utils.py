import os
import socket
import urllib2
import wget as wget_wget
import smtplib
import SimpleHTTPServer
import SocketServer

import logging
log = logging.getLogger(__file__)

import file_utils
import exe_utils

def email(frm, to, msg, subject="loader email"):
    log.info("email: TODO...implement me")

def get_hostname():
    return socket.gethostname()

def basic_web_server(port="50080"):
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", port), Handler)
    print "serving at port", port
    httpd.serve_forever()

def background_web_server(dir=None, port="50080"):
    file_utils.cd(dir)
    ret_val = exe_utils.run_python("-m SimpleHTTPServer " + port, fork=True, pid_file="py_server.pid")
    return ret_val

def my_wget(url, file_path, delete_first=True):
    """ wget a file from url
        IMPORTANT NOTE: this will *not* work if the URL is a redirect, etc...
    """
    is_success = True
    try:
        # get gtfs file from url
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)

        if delete_first:
            file_utils.rm(file_path)

        # write it out
        f = open(file_path, 'wb')
        f.write(res.read())
        f.flush()
        f.close()
        res.close()

        log.info("wget: downloaded {} into file {}".format(url, file_path))
    except Exception, e:
        log.warn(e)
        is_success = False
    return is_success

def wget(url, file_path, delete_first=True):
    """ wget a file from url
        IMPORTANT NOTE: this will *not* work if the URL is a redirect, etc...
    """
    is_success = True
    if delete_first:
        file_utils.rm(file_path)
    wget_wget.download(url, file_path)
    log.info("wget: downloaded {} into file {}".format(url, file_path))
    return is_success

def email(msg,
          mail_server="localhost",
          recipients=[],
          subject="Stand by for a message from OTT...",
          mailfrom="Mr. OTT",
          sender='info@opentransittools.com'):
    """ send an email to someone...
    """
    is_success = True
    message = """ {}
To:  {}
Subject: {}

""".format(sender, recipients, subject)
    try:
        smtp_obj = smtplib.SMTP(mail_server)
        smtp_obj.sendmail(sender, recipients, "From: " + mailfrom + message + msg)
        logging.info('MAIL: From: ' + mailfrom + message + msg)
    except Exception, e:
        log.warn("ERROR: could not send email: {}".format(e))
        is_success = False
    return is_success