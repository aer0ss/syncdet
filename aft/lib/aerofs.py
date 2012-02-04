import os.path, subprocess, sys, time, os
from afterror import AFTError

#######################################
# configurations
FS_NAME         = 'AeroFS'
FS_BIN          = 'aerofs.jar'
WEB_DOWNLOADS   = 'https://www.aerofs.com/staging/downloads'
INSTALLER_LINUX = 'aerofs-installer.deb'
INSTALLER_OSX   = 'AeroFSInstall.dmg'
INSTALLER_WIN   = 'AeroFSInstall.exe'

class AeroError(AFTError): pass

def createAeroFS(): 
    if sys.platform.startswith('linux'):
        return AeroFSonLinux()
    elif sys.platform.startswith('darwin'):
        return AeroFSonOSX()
    #elif sys.platform.startswith('cygwin'):
    else:
        raise NotImplementedError(
                'This module does not support {0}'.format(sys.platform))

class AeroFS:
    _aerofsPrograms = ['cli', 'gui', 'daemon', 'sh', 'fsck']
    _bin = FS_BIN
    _proc = None
    
    def __init__(self, approot, fsroot, rtroot): 
        self._proc = None
        # Must explicitly expand user symbols of these directories, 
        # as the child process does not know to do this
        (self._approot, self._rtroot, self._fsroot) = (
                    os.path.expanduser(r) for r in (approot, fsroot, rtroot)
                                                      )

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

    def install(self): raise NotImplementedError

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
               os.path.join(self.getAppRoot(), self._bin),
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

    def _getInstallerName(): raise NotImplementedError

    # Downloads the AeroFS installer, 
    # * returns the full path of the local installer

    def _downloadInstaller():
        cmd = ['wget', 
               os.path.join(WEB_DOWNLOADS, self._getInstallerName())
              ]
        self._printCmd(cmd)
        try:
            subprocess.check_call(cmd)
        except CalledProcessError, e:
            raise AeroError('Failed download. Error: {0}'.format(e))

        fname = os.path.abspath(self._getInstallerName())
        if not os.path.exists(fname):
            raise AeroError('Installer {0} not found.'.format(fname))

        return fname
            
    def _printCmd(self, cmd): print ' '.join(cmd)


class AeroFSonLinux(AeroFS):
    def __init__(self):
        AeroFS.__init__(self, '~/.aerofs-bin', 
                              '~/.aerofs.staging/AeroFS', 
                              '~/.aerofs.staging')

    # Add the environment variable required only for Linux
    # * note the child process will inherit this environment
    def launch(self, program, args = []):
        os.putenv('LD_LIBRARY_PATH', self._approot)
        AeroFS.launch(self, program, args)

    def install(self):
        fname = self._downloadInstaller()
        # install java
        # install shar utils
        # sudo apt-get -f install
        os.remove(fname)
        
    def _getInstallerName(): return INSTALLER_LINUX

class AeroFSonOSX(AeroFS):
    def __init__(self):
        AeroFS.__init__(self, '/Applications/AeroFS.app/Contents/Resources/Java',
                              '~/Library/Caches/com.aerofs.staging/AeroFS',
                              '~/Library/Caches/com.aerofs.staging')
    def install(self):
        fname = self._downloadInstaller()

        os.remove(fname)

        
    def _getInstallerName(): return INSTALLER_OSX
       

#============================================================================
# Test Code
if __name__ == '__main__':
    af = createAeroFS()
    af.launch('daemon')
    af.terminate()
    # Should fail with an assertion error
    af.terminate()
