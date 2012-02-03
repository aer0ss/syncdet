import os.path, subprocess, sys, time
from afterror import AFTError

#######################################
# configurations
FS_NAME         = 'AeroFS'

class AeroError(AFTError): pass

def createAeroFS(): 
    if sys.platform.startswith('linux'):
        return AeroFS('~/.aerofs-bin', '~/AeroFS', '~/.aerofs')
    elif sys.platform.startswith('darwin'):
        return AeroFS('/Applications/AeroFS.app/Contents/Resources/Java',
                      '~/AeroFS', 
                      '~/Library/Caches/com.aerofs')
    #elif sys.platform.startswith('cygwin'):
    else:
        raise NotImplementedError(
                'This module does not support {0}'.format(sys.platform))

class AeroFS:
    _aerofsPrograms = ['cli', 'gui', 'daemon', 'sh', 'fsck']
    _bin = 'aerofs.jar'
    _rtroot = None
    _approot = None
    _fsroot = None
    _proc = None
    
    def __init__(self, approot, fsroot, rtroot): 
        self._proc = None
        self._approot = approot
        self._rtroot = rtroot
        self._fsroot = fsroot
    

    # Directory where AeroFS libraries/stores live
    #
    def getFSRoot(self): return self._fsroot

    # Directory of AeroFS binaries
    #
    def getAppRoot(self): return self._approot

    # Directory of runtime data (db, logs, etc)
    #
    def getRTRoot(self): return self._fsroot

    # Paths to Daemon and GUI logs
    def getDaemonLog(self): 
        return os.path.join(self.getRTRoot(), 'daemon.log')
    def getGuiLog(self):
        return os.path.join(self.getRTRoot(), 'gui.log')

    # @param program:    string of the program to execute, e.g. daemon or cli
    # @param args:       a list of arguments to AeroFS, not java
    #
    def launch(self, program, args = []):
        javaArgs = []
        if program == 'daemon':
            javaArgs += ['-ea', 
                        '-Xmx64m', 
                        '-XX:+UseConcMarkSweepGC',
                        '-Djava.net.preferIPv4Stack=true']
        self._launch(program, javaArgs, args)
        
    # @param timeout:  permitted time in seconds to gracefully terminate
    #
    def terminate(self, timeout=5): 
        assert self._proc and 'No instance of process'

        # Check if the process is still alive
        ret = self._proc.poll()
        if ret != None:
            raise AeroError(('{0} terminated early with code {1}'
                             ).format(self._bin, ret))

        self._proc.terminate()
        tstart = time.time()
        while not self._proc.poll():
            if time.time() - tstart > timeout:
                self.kill()
                raise AeroError(('{0} termination timeout over {1}s'
                                ).format(self._bin))
            time.sleep(1)

        print 'terminated {1} {0}, with return code {2}'.format(
                self._bin, self._proc.pid, self._proc.poll())
    
        # TODO should I verify anything else, e.g. log file?
        self._proc = None

    def kill(self): 
        try:
            self._proc.kill()
        except OSError, data:
            print data
        self._proc = None

    #========================================================================
    # Helper methods
    def _launch(self, program, javaArgs, args):
        assert program in self._aerofsPrograms
        if self._proc:
            raise AeroError(('{0} has already been launched with pid {1}'
                          ).format(self._bin, self._proc.pid))

        cmd = ['java'] + javaArgs + \
              ['-jar',
               os.path.join(self.getAppRoot(),self._bin),
               'DEFAULT',
               program]
        cmd += args
        self._printCmd(cmd)
        try:
            self._proc = subprocess.Popen(cmd)
        except OSError, e:
            raise AeroError('When executing {1}, error {0}'.format(e,cmd))

        assert self._proc

        # TODO: verify safe/correct launch by looking at log files, 
        #       or communicating with daemon/shell

    def _printCmd(self, cmd): print ' '.join(cmd)



#============================================================================
# Test Code
#af = createAeroFS()
#af.launch('daemon')
#af.terminate()
## Should fail with an assertion error
#af.terminate()
