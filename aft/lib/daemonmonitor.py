import subprocess, threading
from afterror import AFTError

class DaemonMonitorError(AFTError): pass

class DaemonMonitorThread(threading.Thread):
    _proc = None

    # Supply a subprocess.Popen object of the daemon that is running
    def __init__(self, proc):
        threading.Thread.__init__(self)
        self._proc = proc

    def run(self):
        self._proc.wait()
                
        # Should never reach here
        raise DaemonMonitorError(
                ('pid {0} unexpectedly exited with code {1}'
                ).format(self._proc.pid, self._proc.returncode))


#============================================================================
# Test Code
if __name__ == '__main__':
    import time
    # An infinitely running process
    p = subprocess.Popen(['tail', '-f', '/dev/random'])
    dmt = DaemonMonitorThread(p)

    dmt.start()

    time.sleep(5)
    try:
        p.kill()
    #except AFTError, e:
    except DAemonMonitorThread, e:
        pass
