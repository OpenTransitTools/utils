import os
import socket
import subprocess
import filecmp
import datetime
import time

import requests

from ott.utils.config_util import ConfigUtil
from ott.utils import exe_utils
from ott.utils import file_utils
from ott.utils import web_utils

import logging
logging.basicConfig()
log = logging.getLogger(__file__)

# constants
OTP_1 = "1.x"
OTP_2 = "2.x"
OTP_VERSION = OTP_1
OTP_NAME = "otp.jar"
VLOG_NAME = "otp.v"
PID_FILE = "pid.txt"
DEF_GRAPH_NAME="Graph.obj" 

DEF_NAME = "prod"
DEF_PORT = "55555"
DEF_SSL_PORT = "55551"
OTP_DOWNLOAD_URL = "https://repo1.maven.org/maven2/org/opentripplanner/otp/1.3.0/otp-1.3.0-shaded.jar"


def breakout_agency_id(otp_stop_id, agency_id=None):
    """ OTP has <AGENCY_ID>:<STOP_ID> and <AGENCY_ID>:<ROUTE_ID>, so break those apart """
    stop_id = otp_stop_id
    try:
        agency_id, stop_id = otp_stop_id.split(':')
    except Exception as e:
        log.debug(e)
    return agency_id, stop_id


def breakout_transit_modes(mode_str, to_transit="BUS,TRAM,RAIL,GONDOLA", fix_null=True):
    """ OTP 2.x wants to see the mode TRANSIT broken into BUS,TRAM,RAIL,GONDOLA """
    ret_val = mode_str
    if mode_str:
        if 'TRANSIT' in mode_str:
            ret_val = mode_str.replace('TRANSIT', to_transit)
    elif fix_null:
        ret_val = to_transit + ",WALK"
    return ret_val


def make_otp_id(id, agency_id=None):
    """
    OTP TI formats route and stop id as <AGENCY_ID>:<ROUTE_ID> and <AGENCY_ID>:<STOP_ID>
    NOTE: TI also doesn't seem to use proper AGENCY_IDs from GTFS (e.g., no PSC / TRAM in route ids - just TRIMET for all routes)
    """
    ret_val = id
    if agency_id:
        ret_val = "{}:{}".format(agency_id, id)
    return ret_val


def restart_call(call_db_path="call_center/db/call_db.tar.gz", call_runner="call_center/run.sh"):
    """ retstart call-center app
        basically, if we see 'call' a database export (backup) in the call_center folder, we'll assume that call runs
        here and we'll restart the call server from a shell script (all pretty TriMet specific)
    """
    if os.path.isfile(call_db_path):
        subprocess.call([call_runner])


def get_graph_name(otp_version=OTP_VERSION):
    """ return graph name (diff from 1.x and 2.x) """
    ret_val = DEF_GRAPH_NAME
    if otp_version == "2.x":
        ret_val = "graph.obj"
    return ret_val


def get_graph_path(graph_dir, otp_version=OTP_VERSION):
    graph_path = os.path.join(graph_dir, get_graph_name(otp_version))
    return graph_path


def get_otp_path(graph_dir=None, otp_name=OTP_NAME):
    """"return full path to otp.jar"""
    otp_path = os.path.join(graph_dir, otp_name)
    return otp_path


def get_vlog_file_path(graph_dir, vlog_name=VLOG_NAME):
    """return full path to otp.vlog"""
    vlog_path = os.path.join(graph_dir, vlog_name)
    return vlog_path


def get_gtfs_paths(graph_dir=None, gtfs_extension=".zip$"):
    """"return list of full paths to all GTFS files (based on extension) """
    ret_val = []
    gtfs_files = file_utils.ls(graph_dir, gtfs_extension, full_paths=True)
    for f in gtfs_files:
        p = os.path.join(graph_dir, f)
        ret_val.append(p)
    return ret_val


def get_osm_paths(graph_dir=None, osm_extension=".osm$"):
    """"return list of full paths to all OSM files (based on extension) """
    osm_files = file_utils.ls(graph_dir, osm_extension, full_paths=True)
    return osm_files


def get_config_paths(graph_dir=None, osm_extension=".json$"):
    """ return list of full paths to all otp's JSON config files (based on extension) """
    osm_files = file_utils.ls(graph_dir, osm_extension, full_paths=True)
    return osm_files


def get_test_urls_from_config(section='otp', hostname=None, ws_path=None, ws_port=None, app_path=None, app_port=None):
    """ return the OTP map and ws urls from """
    config = ConfigUtil(section=section)

    if not hostname:
        hostname = config.get('host', def_val=web_utils.get_hostname())

    if ws_port is None:
        ws_port = DEF_PORT
    if ws_path is None:
        ws_path = config.get('ws_url_path', def_val="/otp/routers/default/plan")
    ws_url = "http://{}:{}{}".format(hostname, ws_port, ws_path)

    if app_port is None:
        app_port = "80"
    if app_path is None:
        app_path = config.get('app_path', def_val="")
    app_url = "http://{}:{}{}".format(hostname, app_port, app_path)

    return ws_url, app_url


def get_sub_str(s, start_str, end_str=",", def_val=None, return_something=True):
    #import pdb; pdb.set_trace()
    ret_val = def_val
    if start_str in s:
        b = s.index(start_str)
        e = len(s) if end_str not in s else s.index(end_str, b)
        ret_val = s[b : e]
    if return_something and ret_val is None:
        ret_val = s
    return ret_val


def get_otp_version_simple(graph_dir=None, otp_name=OTP_NAME, def_ver=OTP_2):
    """ return the simplified version number """
    ret_val = def_ver
    v,c = get_otp_version(graph_dir, otp_name)
    if v:
        if "version: 2" in v: ret_val = OTP_2
        elif "version: 1" in v: ret_val = OTP_1
    return ret_val


def get_otp_version(graph_dir=None, otp_name=OTP_NAME, otp_version=OTP_VERSION):
    """ find the version and commit strings """
    version = None
    commit = None
    try:
        file_utils.cd(graph_dir)
        otp_path = get_otp_path(graph_dir, otp_name)
        cmd = "java -jar {} --version".format(otp_path)
        stdout = exe_utils.run_cmd_get_stdout(cmd)
        for s in stdout.split("\n"):
            version = get_sub_str(s, 'version', ',', version)
            commit = get_sub_str(s, 'commit', ',', commit)
    except Exception as e:
        log.error(e)
    return version,commit


def build_with_pbf(otp_version):
    return otp_version == OTP_2


def run_graph_builder(graph_dir, otp_version, otp_name=OTP_NAME, java_mem=None):
    """ run OTP graph builder """
    log.info("building the graph")
    otp_path = get_otp_path(graph_dir, otp_name)
    file_utils.cd(graph_dir)
    if otp_version == OTP_2:
        cmd = '-jar {} --build --save --cache {} {}'.format(otp_path, graph_dir, graph_dir)
    else:
        cmd = '-jar {} --build {} --cache {}'.format(otp_path, graph_dir, graph_dir)
    ret_val = exe_utils.run_java(cmd, big_xmx=java_mem)
    return ret_val


def vizualize_graph(graph_dir, otp_version, otp_name=OTP_NAME, java_mem=None):
    otp_path = os.path.join(graph_dir, otp_name)
    file_utils.cd(graph_dir)
    if otp_version == OTP_2:
        cmd = '-jar {} --visualize --load {}'.format(otp_path, graph_dir)
    else:
        cmd = '-jar {} --visualize --router "" --graphs {}'.format(otp_path, graph_dir)
    ret_val = exe_utils.run_java(cmd, big_xmx=java_mem)
    return ret_val


def run_otp_server(graph_dir, otp_version=OTP_VERSION, port=DEF_PORT, ssl=DEF_SSL_PORT, otp_name=OTP_NAME, java_mem=None, **kwargs):
    """ launch the server in a separate process """
    file_utils.cd(graph_dir)
    otp_path = get_otp_path(graph_dir, otp_name)
    if otp_version == OTP_2:
        cmd = '-server -jar {} --port {} --load --serve {}'.format(otp_path, port, graph_dir, graph_dir)
    else:
        cmd = '-server -jar {} --port {} --securePort {} --router "" --graphs {}'.format(otp_path, port, ssl, graph_dir)
    ret_val = exe_utils.run_java(cmd, fork=True, big_xmx=java_mem, pid_file=PID_FILE, echo=True)
    return ret_val


def kill_otp_server(graph_dir):
    pid_path = os.path.join(graph_dir, PID_FILE)
    exe_utils.kill_old_pid(pid_file=pid_path)


def kill(cmd="java", delay=15):
    time.sleep(delay)
    exe_utils.kill_all(cmd)


def call_planner_svc(url, accept='application/xml'):
    """ make a call to the OTP web service """
    # import pdb; pdb.set_trace()
    ret_val = None
    try:
        log.debug("call_otp: OTP output for " + url)
        resp = requests.get(url)
        ret_val = resp.text
        resp.close()
    except Exception as e:
        log.warning('ERROR: could not get data from url (timeout?): {0}'.format(url))
    return ret_val


def wait_for_otp(otp_url, delay=10, max_tries=10, otp_version="1.x"):
    try_count = 0

    otp_is_up = False
    while True:
        try_count += 1
        #import pdb; pdb.set_trace()

        # step 1: call OTP
        response = call_planner_svc(otp_url)

        # step 2: check result ... if valid break out of loop
        matches = ["TripViewerWidget", "requestParameters", "elevationMetadata"]
        otp_is_up = response and any(m in response for m in matches)

        # step 3: either break out of loop or warn an continue checking OTP
        if otp_is_up or try_count > max_tries:
            break
        else:
            log.warn("OTP is not ready yet.\nURL: {}\nWill try again ({} of {} tries) in {} seconds...".format(otp_url, try_count, max_tries, delay))

        time.sleep(delay)

        # step 4: other stopping conditions ... bogus urls, etc....
        if otp_url.startswith("None"):
            log.error("Ruh Roh: url '{}' really don't not much look like a URL".format(otp_url))
            otp_is_up = False
            break

    return otp_is_up


def send_build_test_email(to, build_status=True, test_status=True, server_status=True):
    """ utility to make the graph dir, copy OTP config files into the graph directory, etc...
    """
    #name = graph_config.get('name', DEF_NAME)
    web_utils.simple_email("msg", to)


def config_graph_dir(graph_config, base_dir, overwrite=False):
    """ utility to make the graph dir, copy OTP config files into the graph directory, etc...
    """
    # step 1: get the graph_dir path
    graph_dir = graph_config.get('dir')
    if graph_dir is None:
        name = graph_config.get('name', DEF_NAME)
        graph_dir = os.path.join(base_dir, name)

    # step 2: mkdir (e.g., makes the dir if it doesn't already exist)
    file_utils.mkdir(graph_dir)
    graph_config['dir'] = graph_dir  # save off the full graph dir back object

    # step 3: copy OTP config files
    config_dir = os.path.join(base_dir, "config")
    file_utils.copy_contents(config_dir, graph_dir, overwrite)

    # step 4: check OTP jar exists in config dir
    check_otp_jar(graph_dir)
    return graph_dir


def get_initial_arg_parser(name='otp'):
    """
    make the initial cli argparse for OTP graph building and other fun things
    """
    from ott.utils.parse.cmdline import otp_cmdline
    parser = otp_cmdline.base_parser(prog_name=name)
    otp_cmdline.test_option(parser)
    return parser


def get_graphs(cache):
    """
    routine that both returns the list of graphs, but also (the main
    purpose) add the 'dir' for each graph folder based on graph name
    """
    return get_graphs_from_config(cache.config, cache.this_module_dir)


def get_graphs_from_config(config=None, graph_root_dir='.'):
    """ return the OTP graph info from config --  from
    """
    if config is None:
        config = ConfigUtil(section='otp')

    graphs = config.get_json('graphs')
    if graphs:
        for g in graphs:
            graph_dir = os.path.join(graph_root_dir, g['name'])
            g['dir'] = graph_dir
    return graphs


def find_graph(graphs, find_name):
    """ will build and test each of the graphs we have in self.graphs
    """
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
        log.warning("graphs config was NIL, using default 'prod' graph info")
    else:
        if index >= len(graphs):
            index = 0
            log.warning("graph index of {} exceeds list length, so defaulting to index 0".format(index))
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


def append_vlog_file(graph_dir, feed_msg=None, vlog_name=VLOG_NAME):
    """ print out gtfs feed(s) version numbers and dates to the otp.v log file
    """
    now = datetime.datetime.now().strftime("%B %d, %Y @ %I:%M %p")
    version, commit = get_otp_version(graph_dir)
    msg = "Updated graph ({}, {}) on {} with GTFS feed(s):\n".format(version, commit, now)

    # add any specific feeds messages
    if feed_msg and len(feed_msg) > 0:
        msg = "{}{}\n".format(msg, feed_msg)

    # write message to vlog file
    vlog_path = get_vlog_file_path(graph_dir, vlog_name)
    file_utils.prepend_file(vlog_path, msg)


def diff_vlog_files(svr, graph_dir, vlog_name=VLOG_NAME):
    """ return True if the files are different and need to be redeployed ...

        - grab vlog from remote server that builds new OTP graphs
        - compare it to our local vlog
        - send email if we can't find remote vlog...
    """
    ret_val = False

    # step 1: grab otp.v from build server
    url = "{}/{}".format(svr, vlog_name)
    vlog_path = get_vlog_file_path(graph_dir, vlog_name)
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


def package_new(graph_dir, vlog_name=VLOG_NAME, otp_name=OTP_NAME, otp_version=OTP_VERSION):
    """ copy otp.v, otp.jar and Graph.obj to *-new paths """
    graph_name = get_graph_name(otp_version)
    graph_path = os.path.join(graph_dir, graph_name)
    new_graph_path = file_utils.make_new_path(graph_dir, graph_name)
    file_utils.rm(new_graph_path)
    file_utils.cp(graph_path, new_graph_path)

    vlog_path = os.path.join(graph_dir, vlog_name)
    new_vlog_path = file_utils.make_new_path(graph_dir, vlog_name)
    file_utils.rm(new_vlog_path)
    file_utils.cp(vlog_path, new_vlog_path)

    otp_path = os.path.join(graph_dir, otp_name)
    new_otp_path = file_utils.make_new_path(graph_dir, otp_name)
    file_utils.rm(new_otp_path)
    file_utils.cp(otp_path, new_otp_path)


def rm_new(graph_dir, vlog_name=VLOG_NAME, otp_name=OTP_NAME, otp_version=OTP_VERSION):
    """ remove -new files """
    graph_name = get_graph_name(otp_version)
    graph_path = os.path.join(graph_dir, graph_name)
    new_graph_path = file_utils.make_new_path(graph_dir, graph_name)
    file_utils.rm(new_graph_path)

    vlog_path = os.path.join(graph_dir, vlog_name)
    new_vlog_path = file_utils.make_new_path(graph_dir, vlog_name)
    file_utils.rm(new_vlog_path)

    otp_path = os.path.join(graph_dir, otp_name)
    new_otp_path = file_utils.make_new_path(graph_dir, otp_name)
    file_utils.rm(new_otp_path)


def mv_new_files_into_place(graph_dir, vlog_name=VLOG_NAME, otp_name=OTP_NAME, otp_version=OTP_VERSION):
    """ go thru steps of backing up old graph and moving new graph into place on the server """
    ret_val = False

    graph_name = get_graph_name(otp_version)
    new_graph = file_utils.make_new_path(graph_dir, graph_name)
    new_vlog = file_utils.make_new_path(graph_dir, vlog_name)
    new_otp = file_utils.make_new_path(graph_dir, otp_name)

    # step 1: check if new OTP GRAPH and VLOG exist ... if both do, proceed
    if file_utils.is_min_sized(new_graph, quiet=True) and file_utils.is_min_sized(new_vlog, 20, quiet=True):
        new_otp_exists = file_utils.is_min_sized(new_otp, quiet=True)

        # step 2: current paths
        curr_graph = os.path.join(graph_dir, graph_name)
        curr_vlog = os.path.join(graph_dir, vlog_name)
        curr_otp = os.path.join(graph_dir, otp_name)

        # step 3: create OLD folder and build old paths
        old_path = file_utils.make_old_dir(graph_dir)
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
            log.error("in trying to deploy new graph, I wasn't able to mv old {} (or {}) out of the way".format(curr_graph, curr_otp))
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
                file_utils.mv(new_otp, curr_otp)

            # step 8: last check to make sure we did move things around properly
            if file_utils.is_min_sized(curr_graph) and file_utils.is_min_sized(curr_otp):
                ret_val = True
            else:
                # @todo this should be an email in addtion to a log message
                log.error("ruh roh: after trying to deploy a new graph, I don't see either {} or {}".format(curr_graph, curr_otp))
    return ret_val
