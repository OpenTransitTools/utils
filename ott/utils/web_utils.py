import os
import socket
import urlparse
import urllib2
import httplib
import wget as wget_wget
import smtplib
import SimpleHTTPServer
import SocketServer

import logging
log = logging.getLogger(__file__)

import file_utils
import exe_utils


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

def post(hostname, port, path, data):
    '''
    '''
    #import pdb; pdb.set_trace()
    statuscode = -111
    try:
        webservice = httplib.HTTP(hostname + ":" + port)
        webservice.putrequest("POST", path)
        webservice.putheader("Host", hostname)
        webservice.putheader("Content-type", "text/xml")
        webservice.putheader("Content-length", "%d" % len(data))
        webservice.endheaders()
        webservice.send(data)
        statuscode, statusmessage, header = webservice.getreply()
        log.info("{} :: {} :: {}".format(statuscode, statusmessage, header ))
        #result = webservice.getfile().read()
        #log.info("{}".format(result))
    except Exception, e:
        log.info(e)
    return statuscode

def post_data(url, data):
    '''
    '''
    u = urlparse.urlparse(url)
    return post(u.hostname, u.port, u.path, data)

def post_file(url, file_path):
    """ http post a file to a url
    """
    is_success = False
    try:
        f = open(file_path)
        data = f.read()
        u = urlparse.urlparse(url)
        post(u.hostname, u.port, u.path, data)
        f.close()
    except Exception, e:
        log.info(e)
        is_success = False
    return is_success

def simple_email(msg, to, from_email="mail@opentriptools.com", from_name=None, subject="loader email", mail_server="localhost"):
    ''' simple send email
    '''
    is_success = False

    # step 1: sort out the recipeients of this email and other params
    recipients = []
    for r in to.split(","):
        if "@" not in r:
            log.warn("email: {} doesn't look like an email address, so skipping".format(r))
            continue
        recipients.append(r)

    if not from_name:
        from_name = from_email

    # step 2: send email
    if recipients:
        is_success = email(msg, subject, recipients, from_name, from_email, mail_server)
    return is_success

def email(msg, subject, recipients, from_name, from_email, mail_server):
    """ send an email to someone...
    """
    is_success = True
    message = """ {}
To:  {}
Subject: {}

""".format(from_email, recipients, subject)
    frm = "From: {} {} {}".format(from_name, message, msg)
    try:
        smtp_obj = smtplib.SMTP(mail_server)
        smtp_obj.sendmail(from_email, recipients, frm)
        logging.debug('MAIL: ' + frm)
    except Exception, e:
        log.warn("ERROR: could not send email: {}".format(e))
        is_success = False
    return is_success