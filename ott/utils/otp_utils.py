import os
import socket
import urllib2
import filecmp
import datetime
import logging
log = logging.getLogger(__file__)

from ott.utils import exe_utils
from ott.utils import file_utils
from ott.utils import web_utils


# constants
DEF_NAME   = "prod"
DEF_PORT   = "55555"
DEF_SSL_PORT = "51111"
GRAPH_NAME = "Graph.obj"
OTP_NAME   = "otp.jar"
VLOG_NAME  = "otp.v"
OTP_DOWNLOAD_URL = "http://maven.conveyal.com.s3.amazonaws.com/org/opentripplanner/otp/0.19.0/otp-0.19.0-shaded.jar"


def call_planner_svc(url, accept='application/xml'):
    ret_val = None
    try:
        socket.setdefaulttimeout(2000)
        log.debug("call_otp: OTP output for " + url)
        req = urllib2.Request(url, None, {'Accept':accept})
        res = urllib2.urlopen(req)
        log.debug("call_otp: OTP output for " + url)
        ret_val = res.read()
        res.close()
    except:
        log.warn('ERROR: could not get data from url (timeout?): {0}'.format(url))
    return ret_val

def run_otp_server(dir=None, port=DEF_PORT, ssl=DEF_SSL_PORT, otp_name=OTP_NAME, java_mem=None, **kwargs):
    ''' launch the server in a separate process
    '''
    #import pdb; pdb.set_trace()
    file_utils.cd(dir)
    otp_path = os.path.join(dir, otp_name)
    cmd='-server -jar {} --port {} --securePort {} --router "" --graphs {}'.format(otp_path, port, ssl, dir)
    exe_utils.run_java(cmd, fork=True, big_xmx=java_mem)

def run_graph_builder(graph_dir, graph_name=GRAPH_NAME, otp_name=OTP_NAME, java_mem=None):
    ''' run OTP graph builder
    '''
    log.info("building the graph")
    graph_path = os.path.join(graph_dir, graph_name)
    otp_path = os.path.join(graph_dir, otp_name)
    file_utils.rm(graph_path)
    file_utils.cd(graph_dir)
    cmd='-jar {} --build {} --cache {}'.format(otp_path, graph_dir, graph_dir)
    exe_utils.run_java(cmd, big_xmx=java_mem)

def vizualize_graph(graph_dir, java_mem=None, otp_name=OTP_NAME):
    otp_path = os.path.join(graph_dir, otp_name)
    file_utils.cd(graph_dir)
    cmd='-jar {} --visualize --router "" --graphs {}'.format(otp_path, graph_dir)
    exe_utils.run_java(cmd, fork=True, big_xmx=java_mem)

def config_graph_dir(graph_config, base_dir, force_update=False):
    ''' utility to make the graph dir, copy OTP config files into the graph directory, etc...
    '''
    name = graph_config.get('name', DEF_NAME)
    dir  = graph_config.get('dir',  name)     # optional 'dir' name overrides graph name

    # step 1: mkdir (makes the dir if it doesn't exist)
    graph_dir = os.path.join(base_dir, dir)
    file_utils.mkdir(graph_dir)
    graph_config['dir'] = graph_dir  # save off the full graph dir back struct

    # step 2: copy OTP config files
    config_dir = os.path.join(base_dir, "config")
    file_utils.copy_contents(config_dir, graph_dir, overwrite=force_update)

    # step 3: check OTP jar exists in config dir
    check_otp_jar(graph_dir, force_update=force_update)

    return graph_dir

def get_graph_details(graphs, index=0):
    ''' utility function to find a graph config (e.g., graph folder name, web port, etc...) from self.graphs
        @see [otp] section in config/app.ini
    '''
    ret_val = None
    if graphs is None or len(graphs) < 1:
        ret_val = {"name":DEF_NAME, "port":DEF_PORT, "ssl":DEF_SSL_PORT}
        log.warn("graphs config was NIL, using default 'prod' graph info")
    else:
        if index >= len(graphs):
            index = 0
            log.warn("graph index of {} exceeds list length, so defaulting to index 0".format(index))
        ret_val = graphs[index]
    return ret_val

def check_otp_jar(graph_dir, jar=OTP_NAME, expected_size=50000000, download_url=OTP_DOWNLOAD_URL, force_update=False):
    """ utility to make sure otp.jar exists in the particular graph dir...
        if not, download it
        :return full-path to otp.jar
    """
    jar_path = os.path.join(graph_dir, jar)
    exists = os.path.exists(jar_path)
    if not exists or file_utils.file_size(jar_path) < expected_size or force_update:
        log.info("we don't see OTP {} in {}, so will download {} now".format(jar, graph_dir, download_url))
        web_utils.wget(download_url, jar_path)
    return jar_path

def update_vlog(dir, feed_msg=None, vlog_name=VLOG_NAME):
    """ print out gtfs feed(s) version numbers and dates to the otp.v log file
    """
    #
    msg = "\nUpdated graph on {} with GTFS feed(s):\n".format(datetime.datetime.now().strftime("%B %d, %Y @ %I:%M %p"))

    # add any specific feeds messages
    if feed_msg and len(feed_msg) > 1:
        msg = "{}{}\n".format(msg, feed_msg)

    # write message to vlog file
    vlog = os.path.join(dir, vlog_name)
    f = open(vlog, 'a')
    f.write(msg)
    f.flush()
    f.close()

def diff_vlog(svr, dir, vlog_name=VLOG_NAME):
    """ return True if the files are different and need to be redeployed ...

        - grab vlog from remote server that builds new OTP graphs
        - compare it to our local vlog
        - send email if we can't find remote vlog...
    """
    ret_val = False

    # step 1: grab otp.v from build server
    url = "{}/{}".format(svr, vlog_name)
    vlog_path = os.path.join(dir, vlog_name)
    tmp_vlog_path = vlog_path + ".tmp"
    ok = web_utils.wget(url, tmp_vlog_path, 10)

    if not ok:
        # step 2: remote server doesn't have otp.v exposed ... send an error email...
        msg = "No vlog available at {0}".format(url)
        web_utils.email(msg, msg)
        ret_val = False
    else:
        # step 3: make sure the otp.v we just downloaded has content ... if note, send an error email
        if not exists_and_sized(TMP_VERSION_LOG, 20):
            msg = "vlog file {0} (grabbed from {1}) isn't right ".format(TMP_VERSION_LOG, url)
            email(msg, msg)
            ret_val = False
        else:
            # step 4a: we currently don't have a vlog, so assume we don't have an existing OTP ... let's deploy new download...
            if not exists_and_sized(VERSION_LOG, 20):
                ret_val = True
                logging.info("{0} doesn't exist ... try to grab new OTP from {1} and deploy".format(VERSION_LOG, SVR))
            else:
                # step 4b: check if the vlog files are different...if so, we'll assume the remote is newer and start a new deploy...
                if filecmp.cmp(TMP_VERSION_LOG, VERSION_LOG):
                    logging.info("{0} == {1} ... we're done, going to keep the current graph running".format(VERSION_LOG, TMP_VERSION_LOG))
                else:
                    ret_val = True
                    logging.info("{0} != {1} ... will try to grab new OTP from {2} and deploy".format(VERSION_LOG, TMP_VERSION_LOG, SVR))

    return ret_val

