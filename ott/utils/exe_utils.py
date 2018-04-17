import os
import signal
import subprocess
import time

import object_utils

import logging
log = logging.getLogger(__file__)


def run_python(cmd_line, fork=False, py_cmd="python", shell=None, pid_file=None, log_file=None):
    """ run a python command
    """
    cmd_line = "{} {}".format(py_cmd, cmd_line)
    if shell is None:
        shell = does_cmd_need_a_shell(py_cmd, "--version", fork)
    ret_val = run_cmd(cmd_line, fork, shell, pid_file, log_file)
    return ret_val


def run_java(cmd_line, fork=False, big_xmx="-Xmx4096m", small_xmx="-Xmx1536m", java_cmd="java", shell=None, pid_file=None, log_file=None):
    """ run java ... if we get an exception, try to run again with lower heap size
        @pid_file: send this variable with the name of a file (e.g., "pid.txt") in to get the process pid written out
        NOTE: shell is None NONE None, since we want to test if java can run first w/out an environment
    """
    ret_val = None
    if shell is None:
        shell = does_cmd_need_a_shell(java_cmd, "-version", fork)
    try:
        if big_xmx is None:
            big_xmx = "-Xmx4096m"
        cmd_line = "{} {} {}".format(java_cmd, big_xmx, cmd_line)
        ret_val = run_cmd(cmd_line, fork, shell, pid_file, log_file)
    except Exception as e:
        # try again with smaller java heap memory request
        # NOTE: 'fork' won't get you to see an exception here (because you fork the exception into another process)
        log.info(e)
        cmd_line = "{} {} {}".format(java_cmd, small_xmx, cmd_line)
        ret_val = run_cmd(cmd_line, fork, shell, pid_file, log_file)
    return ret_val


def run_cmd_get_stdout(cmd):
    """ 2.7 way to run things and get output
        @see: http://stackoverflow.com/questions/4760215/running-shell-command-from-python-and-capturing-the-output
    """
    output = subprocess.check_output(cmd, shell=True)
    return output


def does_cmd_need_a_shell(cmd, cmd_line="", fork=False):
    """ does the cmd need a shell to run properly? ...
        if we get thrown an exception, assume that we do need a shell to execute java
    """
    ret_val = False
    cmd = "{} {}".format(cmd, cmd_line)
    try:
        if fork:
            process = subprocess.Popen(cmd, shell=False)
        else:
            process = subprocess.call(cmd, shell=False)
    except:
        ret_val = True
    return ret_val


def write_pid_file(pid_file, pid):
    """ write a pid file
    """
    try:
        if pid_file:
            pf = open(pid_file, 'w')
            pf.write(str(pid))
            pf.flush()
            pf.close()
    except Exception as e:
        log.debug("Couldn't write to the pid file -- {}".format(e))


def run_cmd(cmd_line, fork=False, shell=False, pid_file=None, log_file=None):
    """ run_cmd("sleep 200") will block for 200 seconds
        run_cmd("sleep 200", True) will background the process

        @pid_file: send this variable with the name of a file (e.g., "pid.txt") in to get the process pid written out

        NOTE: some other options for piping output...
          devnull = open(os.devnull, 'wb')
          subprocess.Popen(['nohup', 'sleep', '100'], stdout=devnull, stderr=devnull)
    """
    log.info(cmd_line)
    kill_old_pid(pid_file)

    # append log file cmd to pipe output to that file (should work on both linux and dos)
    if log_file:
        log.debug("changing cmd line {} by appending log file {}".format(cmd_line, log_file))
        cmd_line = "{} > {} 2>&1".format(cmd_line, log_file)
        log.debug("new cmd line: {}".format(cmd_line))

    if fork:
        process = subprocess.Popen(cmd_line, shell=shell)
    else:
        process = subprocess.call(cmd_line, shell=shell)

    # Write PID file
    pid = object_utils.safe_get(process, 'pid')
    write_pid_file(pid_file, pid)
    return pid


def kill_old_pid(pid_file):
    """ read pid file and then kill process
    """
    try:
        pf = open(pid_file, 'r')
        pid = pf.read().strip()
        if pid and len(pid) > 1:
            kill(pid)
            time.sleep(5)
    except Exception as e:
        log.debug(e)


def kill(pid):
    """ kill a process
    """
    #import pdb; pdb.set_trace()
    try:
        log.debug("trying to kill pid {}".format(pid))
        os.kill(int(pid), signal.SIGKILL)
    except Exception as e:
        log.debug(e)
        try:
            win_kill = "taskkill /pid {} /f".format(pid)
            log.debug("WINDOWS? will try to kill via: {}".format(win_kill))
            os.system(win_kill)
        except Exception as e:
            log.debug(e)


def find_executable(name):
    ret_val = None
    try:
        ret_val = find_executable_distutils(name)
    except Exception as e:
        pass
    return ret_val


def find_executable_distutils(name):
    ret_val = None
    try:
        import distutils.spawn
        ret_val = distutils.spawn.find_executable(name)
        if ret_val is None:
            ret_val = distutils.spawn.find_executable(name + ".exe")
    except Exception as e:
        pass
    return ret_val

