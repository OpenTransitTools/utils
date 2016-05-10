import logging
log = logging.getLogger(__file__)


def run_java(cmd_line, fork=False, big_xmx="-Xmx4096m", small_xmx="-Xmx1500m", java_cmd="java"):
    try:
        java_cmd = "{} {} {}".format(java_cmd, big_xmx, cmd_line)
        run_cmd(java_cmd, fork)
    except Exception, e:
        log.info(e)
        java_cmd = "{} {} {}".format(java_cmd, small_xmx, cmd_line)
        run_cmd(java_cmd, fork)

def run_cmd(cmd_line, fork=False):
    ''' run_cmd("sleep 200") will block for 200 seconds
        run_cmd("sleep 200", True) will background

        NOTE: some other options for piping output...
        devnull = open(os.devnull, 'wb')
        subprocess.Popen(['nohup', 'sleep', '100'], stdout=devnull, stderr=devnull)
    '''
    log.info(cmd_line)
    if fork:
        subprocess.Popen(cmd_line.split())
    else:
        os.system(cmd_line)
