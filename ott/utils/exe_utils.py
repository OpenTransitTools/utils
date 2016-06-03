import os
import subprocess
import logging
log = logging.getLogger(__file__)


def run_java(cmd_line, fork=False, big_xmx="-Xmx4096m", small_xmx="-Xmx1536m", java_cmd="java", shell=True, pid_file=True):
    ''' run java ... if we get an exception, try to run again with lower heap size
    '''
    #import pdb; pdb.set_trace()
    try:
        if big_xmx is None:
            big_xmx = "-Xmx4096m"
        java_cmd = "{} {} {}".format(java_cmd, big_xmx, cmd_line)
        run_cmd(java_cmd, fork, shell, pid_file)
    except Exception, e:
        # NOTE: 'fork' won't get you to see an exception here (because you fork the exception into another process)
        log.info(e)
        # try again with smaller java heap memory request
        java_cmd = "{} {} {}".format(java_cmd, small_xmx, cmd_line)
        run_cmd(java_cmd, fork, shell, pid_file)
        pass

def run_cmd(cmd_line, fork=False, shell=True, pid_file=True):
    ''' run_cmd("sleep 200") will block for 200 seconds
        run_cmd("sleep 200", True) will background

        NOTE: some other options for piping output...
          devnull = open(os.devnull, 'wb')
          subprocess.Popen(['nohup', 'sleep', '100'], stdout=devnull, stderr=devnull)
    '''
    log.info(cmd_line)
    if fork:
        process = subprocess.Popen(cmd_line, shell=shell)
    else:
        process = subprocess.call(cmd_line, shell=shell)

    # Write PID file
    write_pid_file(pid_file)

    return process.pid

def write_pid_file(pid_file):
    ''' write a pid file
    '''
    if pid_file:
        pf = open(pid_file, 'w')
        pf.write(str(process.pid))
        pf.close()
