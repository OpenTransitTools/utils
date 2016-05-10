import os
import subprocess
import logging
log = logging.getLogger(__file__)


def run_java(cmd_line, fork=False, big_xmx="-Xmx4096m", small_xmx="-Xmx1536m", java_cmd="java"):
    ''' run java ... if we get an exception, try to run again with lower heap size
    '''
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

def wget(url, file_name):
    """ wget a file from url
        IMPORTANT NOTE: this will *not* work if the URL is a redirect, etc...
    """
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

