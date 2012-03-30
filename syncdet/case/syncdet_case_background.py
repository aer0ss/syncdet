import subprocess
from case import getLogFilePath, getLogFolderPath, getActorId
import syncdet_lib
import os, signal

def startBackgroundProcess(cmd, key = None):
    """Run a command in a separate process, which can be terminated by
    stopBackgroundProcess() from a process different from the current one.

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

    if key is None: key = cmd[0]

    # launch the process
    with open(getLogFilePath(key), 'a') as f:
        p = subprocess.Popen(cmd, 0, None, f, f)

    # write the pid file
    with open(getPIDFilePath(key), 'w') as f:
        f.write(str(p.pid))

    return p

def stopBackgroundProcess(key):
    '''Stop a background process specified by the key. The process must be
    launched by startBackgroundProcess(). The method sends SIGKILL to the
    process and returns immediately.'''
    pathPID = getPIDFilePath(key)
    with open(pathPID) as f:
        for line in f:
            pid = int(line)
            os.kill(pid, signal.SIGKILL)
    os.remove(pathPID)

def getPIDFilePath(key):
    return syncdet_lib.getPIDFilePath(getLogFolderPath(), key, getActorId())
