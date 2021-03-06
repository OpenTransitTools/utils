import socket
import smtplib

from .compat_2_to_3 import *
from . import file_utils
from . import exe_utils

import logging
log = logging.getLogger(__file__)


def get_hostname():
    return socket.gethostname()


def get_name_from_url(url, def_name=None):
    ret_val = def_name
    try:
        ret_val = urlsplit(url).path.split('/')[-1]
    except Exception as e:
        log.warning(e)
    return ret_val


def make_url(hostname, port=None, path=None, arg_str=None, def_hostname="http://127.0.0.1"):
    ret_val = None

    # step 1: make sure hostname is valid
    if hostname is None:
        hostname = def_hostname
    elif not hostname.startswith('http'):
        hostname = "http://{}".format(hostname)

    # step 2: fix ports
    if port and port != '80':
        ret_val = "{}:{}".format(hostname, port)
    else:
        ret_val = hostname

    # step 3: add path to url
    if path and len(path) > 0:
        ret_val = "{}/{}".format(ret_val.rstrip('/'), path.lstrip('/'))
    if arg_str and len(arg_str) > 0:
        ret_val = "{}?{}".format(ret_val, arg_str)

    return ret_val


def basic_web_server(port=50080):
    print("NOTE: TODO - THIS WON'T WORK ON PY 3.x")
    import SimpleHTTPServer
    import SocketServer
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", int(port)), Handler)
    print("serving at port {}".format(port))
    httpd.serve_forever()
    return httpd


def background_web_server(dir=None, port="50080"):
    file_utils.cd(dir)
    ret_val = exe_utils.run_python("-m SimpleHTTPServer " + port, fork=True, pid_file="py_server.pid")
    return ret_val


def my_wget(url, file_path=None, delete_first=True):
    """ wget a file from url
        IMPORTANT NOTE: this will *not* work if the URL is a redirect, etc...
    """
    is_success = True
    try:
        # get gtfs file from url
        req = urllib.request.Request(url)
        res = urllib.request.urlopen(req)

        if delete_first:
            file_utils.rm(file_path)

        if file_path is None:
            file_path = file_utils.get_file_name_from_url(url)

        # write it out
        f = open(file_path, 'wb')
        f.write(res.read())
        f.flush()
        f.close()
        res.close()

        log.info("wget: downloaded {} into file {}".format(url, file_path))
    except Exception as e:
        log.warning(e)
        is_success = False
    return is_success


def wget(url, file_path=None, delete_first=True):
    """ wget a file from url
        IMPORTANT NOTE: this will *not* work if the URL is a redirect, etc...
        IMPORTANT NOTE 2: you need to have requests package installed ...
    """
    import requests

    is_success = True
    if delete_first:
        file_utils.rm(file_path)

    if file_path is None:
        file_path = file_utils.get_file_name_from_url(url)

    log.info("wget: downloaded {} into file {}".format(url, file_path))
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.107 Safari/537.36',
               'Upgrade-Insecure-Requests': '1',
               'x-runtime': '148ms'}
    r = requests.get(url, headers=headers, allow_redirects=True, stream=True)
    with open(file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return is_success


def scp_client(host, user, password=None):
    """ return the 'scp' & 'ssh' clients (ssh probably not needed, but if it loses scope the tunnel gets closed)
        NOTE: caller is responsible to call scp.close() on this object
    """
    import paramiko
    from scp import SCPClient

    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if password:
        ssh.connect(host, username=user, password=password)
    else:
        # assumes that the two servers have a trust relationship ala known_hosts file
        ssh.connect(host, username=user)

    scp = SCPClient(ssh.get_transport())
    return scp, ssh


def flash(cmd):
    if cmd == "docker":
        exe_utils.run_cmd_get_stdout("docker kill $(docker ps -aq)")
    elif cmd == "python":
        exe_utils.kill_all("python")
        exe_utils.kill_all("python3")
        exe_utils.kill_all("pserve")
    else:
        exe_utils.kill_all(cmd)


def post(hostname, port, path, data):
    """
    """
    statuscode = -111
    try:
        import httplib  # TODO ... this won't work on py 3
        webservice = httplib.HTTP("{}:{}".format(hostname, port))
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
    except Exception as e:
        log.warning(e)
        log.warning("FIX ME -- py 3.x -- httplib")
    return statuscode


def post_data(url, data):
    """
    """
    u = urlparse.urlparse(url)
    return post(u.hostname, u.port, u.path, data)


def post_file(url, file_path):
    """ http post a file to a url
    """
    try:
        f = open(file_path, "r")
        data = f.read()
        u = urlparse.urlparse(url)
        statuscode = post(u.hostname, u.port, u.path, data)
        f.close()
    except Exception as e:
        statuscode = -111
        log.warning(e)
    return statuscode


def get(url):
    """ safe http get of url, with return of
    """
    success = True
    response = None
    try:
        response = urllib.request.urlopen(url)
    except Exception as e:
        log.warning(e)
        success = False
    return success, response


def get_response(url, show_info=False):
    """ safe / simple get response
    """
    ret_val = None
    response = None
    try:
        success, response = get(url)
        if show_info:
            ret_val = "INFO:\n{}\n\nRESPONSE:\n{}".format(response.info(), response.read())
        else:
            ret_val = "{}\n".format(response.read())
    except Exception as e:
        log.warning(e)
    finally:
        if response:
            response.close()
    return ret_val


def write_url_response_file(file_path, url, response):
    """ write url atop a file, and the response body below...
        will looks something like:
            http://maps7:80/prod?submit&module=planner&fromPlace=ME::45.468019,-122.655552&toPlace=OHSU::45.499049,-122.684283&maxWalkDistance=840&optimize=QUICK&time=10:00AM&date=11-02-2016

            INFO:
            Date: Wed, 02 Nov 2016 21:01:35 GMT
            Access-Control-Allow-Origin: *

            RESPONSE:
            {"requestParameters":{"date":"11-02-2016","submit":"","optimize":"QUICK","fromPlace":"ME::45.468019,-12...
    """
    f = None
    try:
        f = open(file_path, 'w')
        f.write(url)
        f.write("\n\n")
        f.write(response)
        f.write("\n")
    except Exception as e:
        log.warning(e)
    finally:
        if f is not None:
            f.close()


def simple_email(msg, to, from_email="mail@opentriptools.com", subject="loader email", mail_server="localhost"):
    """ simple send email
    """
    is_success = False

    # step 1: sort out the recipeients of this email and other params
    recipients = []
    for r in to.split(","):
        if "@" not in r:
            log.info("email: {} doesn't look like an email address, so skipping".format(r))
            continue
        recipients.append(r)

    # step 2: send email
    if recipients:
        is_success = email(msg, subject, recipients, from_email, mail_server)
    return is_success


def email(msg, subject, recipients, from_email, mail_server):
    """ send an email to someone...
    """
    # import pdb; pdb.set_trace()
    is_success = False
    message = """From: {}
To:  {}
Subject: {}

{}

""".format(from_email, ','.join(recipients), subject, msg)

    try:
        smtp_obj = smtplib.SMTP(mail_server)
        smtp_obj.sendmail(from_email, recipients, message)
        logging.debug('MAIL: ' + message)
        is_success = True
    except Exception as e:
        log.warning("ERROR: could not send email: {}".format(e))
        is_success = False
    return is_success
