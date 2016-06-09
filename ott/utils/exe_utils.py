import os
import signal
import subprocess
import time
import logging
log = logging.getLogger(__file__)


def run_java(cmd_line, fork=False, big_xmx="-Xmx4096m", small_xmx="-Xmx1536m", java_cmd="java", shell=None, pid_file="pid.txt"):
    ''' run java ... if we get an exception, try to run again with lower heap size
        NOTE: shell is None here by default, so we can detect whether java needs a shell to operate (ala maps servers)
    '''
    if shell is None:
        shell = does_java_need_a_shell(java_cmd, fork)
    try:
        if big_xmx is None:
            big_xmx = "-Xmx4096m"
        cmd_line = "{} {} {}".format(java_cmd, big_xmx, cmd_line)
        run_cmd(cmd_line, fork, shell, pid_file)
    except Exception, e:
        # try again with smaller java heap memory request
        # NOTE: 'fork' won't get you to see an exception here (because you fork the exception into another process)
        log.info(e)
        cmd_line = "{} {} {}".format(java_cmd, small_xmx, cmd_line)
        run_cmd(cmd_line, fork, shell, pid_file)


def does_java_need_a_shell(java_cmd):
    ''' does java cmd need a shell to run properly? ...
        if we get thrown an exception, assume that we do need a shell to execute java
    '''
    ret_val = False
    try:
        if fork:
            process = subprocess.Popen(cmd_line, shell=False)
        else:
            process = subprocess.call(cmd_line, shell=False)
    except:
        ret_val = True
    return ret_val


def run_cmd(cmd_line, fork=False, shell=False, pid_file="pid.txt"):
    ''' run_cmd("sleep 200") will block for 200 seconds
        run_cmd("sleep 200", True) will background

        NOTE: some other options for piping output...
          devnull = open(os.devnull, 'wb')
          subprocess.Popen(['nohup', 'sleep', '100'], stdout=devnull, stderr=devnull)
    '''
    log.info(cmd_line)
    kill_old_pid(pid_file)
    if fork:
        process = subprocess.Popen(cmd_line, shell=shell)
    else:
        process = subprocess.call(cmd_line, shell=shell)

    # Write PID file
    pid = None
    if process and process.pid:
        pid = process.pid
        write_pid_file(pid_file, pid)
    return pid


def kill_old_pid(pid_file):
    ''' read pid file and then kill process
    '''
    try:
        pf = open(pid_file, 'r')
        pid = pf.read().strip()
        if pid and len(pid) > 1:
            kill(pid)
            time.sleep(5)
    except Exception, e:
        log.debug(e)


def write_pid_file(pid_file, pid):
    ''' write a pid file
    '''
    pf = open(pid_file, 'w')
    pf.write(str(pid))
    pf.flush()
    pf.close()


def kill(pid):
    ''' kill a process
    '''
    #import pdb; pdb.set_trace()
    try:
        os.kill(int(pid), signal.SIGKILL)
    except Exception, e:
        log.debug(e)
        try:
            win_kill = "taskkill /pid {} /f".format(pid)
            log.debug("WINDOWS? will try to kill via: {}".format(win_kill))
            os.system(win_kill)
        except Exception, e:
            log.debug(e)
