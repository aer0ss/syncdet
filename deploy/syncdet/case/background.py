import subprocess, os, signal
from .. import lib, case
import sys

def start_process(cmd, key=None, env=None):
    """Run a command in a separate process, which can be terminated by
    stop_process() from a process different from the current one.

    @param cmd: list of strings representing  a command with arguments.
    e.g. ["/bin/sleep", "5"]
    @param key: the key of the process, will be used in the log file name. Also
    used by stopDaemon() to identify the process. When None, cmd[0] will be
    used as the key. Note that to start multiple processes of the same command,
    different keys must be used, otherwise the result would be unpredicted.
    @return: a subprocess.Popen object that represents the subprocess

    The stdout and stderr of the subprocess are redirected to a log file which
    can be found under the same folder of the test case's log.
    """

    if key is None:
        key = cmd[0]

    path_pid = _get_pid_file_path(key)
    if os.path.exists(path_pid):
        pid = _read_pid_file(path_pid)
        print('WARNING: a background process "{0}" launched previously'
              ' might not have been properly stopped. PID: {1}'
              .format(key, pid))

    # launch the process
    with open(case.log_file_path(key), 'a') as f:
        if 'win32' in sys.platform:
            p = subprocess.Popen(cmd, bufsize=0, close_fds=True, env=env, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            p = subprocess.Popen(cmd, bufsize=0, stdin=None, stdout=f, stderr=subprocess.STDOUT, env=env)
    # write the pid file
    with open(path_pid, 'w') as f:
        f.write(str(p.pid))

    return p

def stop_process(key, ignore_kill_error=False):
    """
    Stop a background process specified by the key. The process must be
    launched by start_process(). The method sends SIGKILL to the
    process and returns immediately.
    @param ignore_kill_error whether or not to ignore errors during kill()
    """
    path_pid = _get_pid_file_path(key)
    pid = _read_pid_file(path_pid)
    try:
        os.kill(pid, signal.SIGKILL)
    except:
        if not ignore_kill_error:
            raise sys.exc_info()[1]
    os.remove(path_pid)

def _read_pid_file(path_pid):
    """
    Return the PID written in the file. Return None if the file is empty
    """
    with open(path_pid) as f:
        for line in f:
            pid = int(line)
            return pid

def _get_pid_file_path(key):
    """
    Return the PID file path and create the parent folder if not found
    """
    path = lib.background_pid_file(case.root_path(), key)
    parent = os.path.dirname(path)
    if not os.path.exists(parent):
        os.makedirs(parent)
    return path
