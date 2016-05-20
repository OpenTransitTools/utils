import os
import logging
log = logging.getLogger(__file__)

from ott.utils import file_utils
from ott.utils import exe_utils

# constants
DEF_NAME   = "prod"
DEF_PORT   = "55555"
OTP_DOWNLOAD_URL="http://maven.conveyal.com.s3.amazonaws.com/org/opentripplanner/otp/0.19.0/otp-0.19.0-shaded.jar"
OTP_NAME="otp.jar"

GRAPH_NAME = "Graph.obj"


def run_otp_server(graph_dir, port="8080", otp_name=OTP_NAME, java_mem=None):
    ''' launch the server in a separate process
    '''
    file_utils.cd(graph_dir)
    otp_path = os.path.join(graph_dir, otp_name)
    cmd='-server -jar {} --port {} --router "" --graphs {}'.format(otp_path, port, graph_dir)
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

def vizualize_graph(graph_dir, java_mem=None):
    otp_path = os.path.join(graph_dir, otp_name)
    file_utils.cd(graph_dir)
    cmd='-jar {} --visualize --router "" --graphs {}'.format(otp_path, graph_dir)
    exe_utils.run_java(cmd, fork=True, big_xmx=java_mem)

def config_graph_dir(graph_config, base_dir):
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
    file_utils.copy_contents(config_dir, graph_dir, overwrite=False)

    # step 3: check OTP jar exists in config dir
    check_otp_jar(graph_dir)

    return graph_dir

def get_graph_details(graphs, index=0):
    ''' utility function to find a graph config (e.g., graph folder name, web port, etc...) from self.graphs
        @see [otp] section in config/app.ini
    '''
    ret_val = None
    if graphs is None or len(graphs) < 1:
        ret_val = {"name":DEF_NAME, "port":DEF_PORT}
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
        exe_utils.wget(download_url, jar_path)
    return jar_path

