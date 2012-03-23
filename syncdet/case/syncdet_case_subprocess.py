import subprocess, sys
from threading import Thread

class WaitingThread(Thread):

    p = None

    def __init__(self, p):
        Thread.__init__(self)
        self.p = p

    def run(self):
        self.p.wait()

def startSubprocess(args):
    """Run command with arguments. Both the command and arguments are specified
    in args, e.g. ["/bin/sleep", "5"]

    Return a subprocess.Popen object that represents the subprocess

    The stdout and stderr of the subprocess are redirected to the current 
    process's stdout and stderr.
    
    A new, non-daemon thread is created to wait for the subprocess to complete.
    Therefore, not terminating the subprocess would prevent the current process
    from terminating, and thus cause the test case to time out.
    
    Important: do NOT call sys.exit() in test cases to prevent orphan 
    subprocesses intervening with subsequent test cases.    
    """

    p = subprocess.Popen(args, 0, None, sys.stdout, sys.stderr)

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
