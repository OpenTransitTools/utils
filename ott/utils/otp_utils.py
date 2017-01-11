import os
import socket
import subprocess
import urllib2
import filecmp
import datetime
import logging
log = logging.getLogger(__file__)

from ott.utils.config_util import ConfigUtil
from ott.utils import exe_utils
from ott.utils import file_utils
from ott.utils import web_utils


# constants
DEF_NAME   = "prod"
DEF_PORT   = "55555"
DEF_SSL_PORT = "55551"
GRAPH_NAME = "Graph.obj"
OTP_NAME   = "otp.jar"
VLOG_NAME  = "otp.v"
OTP_DOWNLOAD_URL = "http://maven.conveyal.com.s3.amazonaws.com/org/opentripplanner/otp/0.20.0/otp-0.20.0-shaded.jar"


def restart_call(self, call_db_path="call_center/db/call_db.tar.gz", call_runner="call_center/run.sh"):
    """ retstart call-center app
        basically, if we see 'call' a database export (backup) in the call_center folder, we'll assume that call runs
        here and we'll restart the call server from a shell script (all pretty TriMet specific)
    """
    if os.path.isfile(call_db_path):
        subprocess.call([call_runner])


def get_test_urls_from_config(section='otp', port=None, hostname=None, ws_path=None, map_path=None):
    """ return the OTP map and ws urls from
    """
    #import pdb; pdb.set_trace()
    config = ConfigUtil(section=section)

    if not hostname:
        hostname = config.get('host', def_val=web_utils.get_hostname())
    if not port:
        port = DEF_PORT

    if ws_path is None:
        ws_path = config.get('ws_url_path', def_val="/otp/routers/default/plan")
    ws_url = "http://{}:{}{}".format(hostname, port, ws_path)

    if map_path is None:
        map_path = config.get('map_url_path', def_val="")
    map_url = "http://{}:{}{}".format(hostname, port, map_path)

    return ws_url, map_url


def call_planner_svc(url, accept='application/xml'):
    """ make a call to the OTP web service
    """
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
    """ launch the server in a separate process
    """
    file_utils.cd(dir)
    otp_path = os.path.join(dir, otp_name)
    cmd='-server -jar {} --port {} --securePort {} --router "" --graphs {}'.format(otp_path, port, ssl, dir)
    ret_val = exe_utils.run_java(cmd, fork=True, big_xmx=java_mem, pid_file="pid.txt")
    return ret_val


def run_graph_builder(graph_dir, graph_name=GRAPH_NAME, otp_name=OTP_NAME, java_mem=None):
    """ run OTP graph builder
    """
    log.info("building the graph")
    graph_path = os.path.join(graph_dir, graph_name)
    otp_path = os.path.join(graph_dir, otp_name)
    file_utils.rm(graph_path)
    file_utils.cd(graph_dir)
    cmd='-jar {} --build {} --cache {}'.format(otp_path, graph_dir, graph_dir)
    ret_val = exe_utils.run_java(cmd, big_xmx=java_mem)
    return ret_val


def vizualize_graph(graph_dir, java_mem=None, otp_name=OTP_NAME):
    otp_path = os.path.join(graph_dir, otp_name)
    file_utils.cd(graph_dir)
    cmd='-jar {} --visualize --router "" --graphs {}'.format(otp_path, graph_dir)
    ret_val = exe_utils.run_java(cmd, big_xmx=java_mem)
    return ret_val


def send_build_test_email(to, build_status=True, test_status=True, server_status=True):
    """ utility to make the graph dir, copy OTP config files into the graph directory, etc...
    """
    #name = graph_config.get('name', DEF_NAME)
    web_utils.simple_email("msg", to)


def config_graph_dir(graph_config, base_dir, overwrite=False):
    """ utility to make the graph dir, copy OTP config files into the graph directory, etc...
    """
    name = graph_config.get('name', DEF_NAME)
    dir  = graph_config.get('dir',  name)     # optional 'dir' name overrides graph name

    # step 1: mkdir (makes the dir if it doesn't exist)
    graph_dir = os.path.join(base_dir, dir)
    file_utils.mkdir(graph_dir)
    graph_config['dir'] = graph_dir  # save off the full graph dir back struct

    # step 2: copy OTP config files
    config_dir = os.path.join(base_dir, "config")
    file_utils.copy_contents(config_dir, graph_dir, overwrite)

    # step 3: check OTP jar exists in config dir
    check_otp_jar(graph_dir)
    return graph_dir


def get_initial_arg_parser():
    """ make the initial cli argparse for OTP graph building and other fun things
    """
    import argparse
    parser = argparse.ArgumentParser(prog='otp-build', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('name', default="all", nargs='?', help="Name of OTP graph folder in the 'cache' build (e.g., 'all', 'prod', 'test' or 'call')")
    parser.add_argument('--test_suite', '-ts', help="regex name of test suites to run (e.g., 'rail', 'bus|rail', etc...)")
    return parser


def get_graphs(cache):
    """ routine that both returns the list of graphs, but also (the main
        purpose) add the 'dir' for each graph folder based on graph name
    """
    return get_graphs_from_config(cache.config, cache.this_module_dir)


def get_graphs_from_config(config=None, graph_root_dir='.'):
    """ return the OTP graph info from config --  from
    """
    if config is None:
        config = ConfigUtil(section='otp')

    graphs = config.get_json('graphs')
    for g in graphs:
        dir = os.path.join(graph_root_dir, g['name'])
        g['dir'] = dir
    return graphs


def find_graph(graphs, find_name):
    """ will build and test each of the graphs we have in self.graphs
    """
    #import pdb; pdb.set_trace()
    ret_val = None
    if graphs is None or len(graphs) < 1:
        ret_val = get_graph_details(None)
    else:
        for g in graphs:
            if find_name in g['name']:
                ret_val = g
                break
    return ret_val


def get_graph_details(graphs, index=0):
    """ utility function to find a graph config (e.g., graph folder name, web port, etc...) from self.graphs
        @see [otp] section in config/app.ini
    """
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


def check_otp_jar(graph_dir, jar=OTP_NAME, expected_size=50000000, download_url=OTP_DOWNLOAD_URL):
    """ utility to make sure otp.jar exists in the particular graph dir...
        if not, download it
        :return full-path to otp.jar
    """
    jar_path = os.path.join(graph_dir, jar)
    exists = os.path.exists(jar_path)
    if not exists or file_utils.file_size(jar_path) < expected_size:
        log.info("we don't see OTP {} in {}, so will download {} now".format(jar, graph_dir, download_url))
        web_utils.wget(download_url, jar_path)
    return jar_path


def append_vlog_file(dir, feed_msg=None, vlog_name=VLOG_NAME):
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


def diff_vlog_files(svr, dir, vlog_name=VLOG_NAME):
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
        # step 3: make sure the otp.v we just downloaded has content ... if not, send an error email
        if not file_utils.is_min_sized(tmp_vlog_path, 20):
            msg = "vlog file {0} (grabbed from {1}) isn't right ".format(tmp_vlog_path, url)
            email(msg, msg)
            ret_val = False
        else:
            # step 4a: we currently don't have a vlog, so assume we don't have an existing OTP ... let's deploy new download...
            if not file_utils.is_min_sized(vlog_path, 20):
                ret_val = True
                logging.info("{0} doesn't exist ... try to grab new OTP from {1} and deploy".format(vlog_path, svr))
            else:
                # step 4b: check if the vlog files are different...if so, we'll assume the remote is newer and start a new deploy...
                if filecmp.cmp(tmp_vlog_path, vlog_path):
                    logging.info("{0} == {1} ... we're done, going to keep the current graph running".format(tmp_vlog_path, vlog_path))
                else:
                    ret_val = True
                    logging.info("{0} != {1} ... will try to grab new OTP from {2} and deploy".format(tmp_vlog_path, vlog_path, svr))
    return ret_val


def deploy_new_otp_graph(dir, graph_name=GRAPH_NAME, vlog_name=VLOG_NAME, otp_name=OTP_NAME):
    """ go thru steps of backing up old graph and moving new graph into place
    """
    ret_val = False

    new_graph = file_utils.make_new_path(dir, graph_name)
    new_vlog = file_utils.make_new_path(dir, vlog_name)
    new_otp = file_utils.make_new_path(dir, otp_name)

    # step 1: check if new OTP GRAPH and VLOG exist ... if both do, proceed
    if file_utils.is_min_sized(new_graph, quiet=True) and file_utils.is_min_sized(new_vlog, 20, quiet=True):
        new_otp_exists = file_utils.is_min_sized(new_otp, quiet=True)

        # step 2: have a place to put old stuff into
        old_path = file_utils.make_old_dir(dir)

        # step 3a: current paths
        curr_graph = os.path.join(dir, graph_name)
        curr_vlog = os.path.join(dir, vlog_name)
        curr_otp = os.path.join(dir, otp_name)

        # step 3b: old paths
        old_graph = os.path.join(old_path, graph_name)
        old_vlog = os.path.join(old_path, vlog_name)
        old_otp = os.path.join(old_path, otp_name)

        # step 4: mv current stuff to the OLD directory
        file_utils.mv(curr_graph, old_graph)
        if new_otp_exists:
            file_utils.mv(curr_otp, old_otp)

        # step 5: make sure we moved old stuff out of the way ... if not, we have to exit
        if file_utils.is_min_sized(curr_graph, quiet=True) or (new_otp_exists and file_utils.is_min_sized(curr_otp, quiet=True)):
            # @todo this should be an email in addtion to a log message
            log.error("in trying to deploy new graph, I wasn't able to mv old {} (or {}) out of the way".format(curr_graph,                                                                                                            curr_otp))
        else:
            # step 6: ok, we could move the graph (and maybe otp) to OLD dir ... now let's back those files up (rename with date stamp)
            file_utils.mv(curr_vlog, old_vlog)
            file_utils.bkup(old_vlog)
            file_utils.bkup(old_graph)
            if new_otp_exists:
                file_utils.bkup(old_otp)

            # step 7: move new stuff into the 'current' position
            file_utils.mv(new_graph, curr_graph)
            file_utils.mv(new_vlog, curr_vlog)
            if new_otp_exists:
                file_utils.mv(new_vlog, curr_otp)

            # step 8: last check to make sure we did move things around properly
            if file_utils.is_min_sized(curr_graph) and file_utils.is_min_sized(curr_otp):
                ret_val = True
            else:
                # @todo this should be an email in addtion to a log message
                log.error("ruh roh: after trying to deploy a new graph, I don't see either {} or {}".format(curr_graph, curr_otp))

    return ret_val