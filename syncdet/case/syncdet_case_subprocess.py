import subprocess
from threading import Thread
from case import getLogFilePath

class WaitingThread(Thread):

    p = None

    def __init__(self, p):
        Thread.__init__(self)
        self.p = p

    def run(self):
        self.p.wait()

def startSubprocess(cmd, name = None):
    """Run command in a separate process.
    
    @param cmd: list of strings representing  a command with arguments. 
    e.g. ["/bin/sleep", "5"]
    @param name: the name of the process, will be used in the log file name.
    When None, the cmd[0] will be used as the name.
    @return: a subprocess.Popen object that represents the subprocess

    The stdout and stderr of the subprocess are redirected to a log file which
    can be found under the same folder of the test case's log.
    
    A new, non-daemon thread is created to wait for the subprocess to complete.
    Therefore, not terminating the subprocess would prevent the current process
    from terminating, and thus cause the test case to time out.
    
    Important: do NOT call sys.exit() in test cases to prevent orphan 
    subprocesses intervening with subsequent test cases.    
    """

    if name is None:
        name = cmd[0]

    f = open(getLogFilePath('-subprocess.' + name), 'a')
    p = subprocess.Popen(cmd, 0, None, f, f)

    thd = WaitingThread(p);
    thd.setDaemon(False)
    thd.start()

    return p

########
# Test

if __name__ == '__main__':
    print "start an infinitely running process"
    p = startSubprocess(['od', '/dev/random'])
    print "kill "
    p.kill()
    print "now the current process should terminate"
