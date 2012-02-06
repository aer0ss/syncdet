import os.path, subprocess, sys, time, os
from os.path import join
from afterror import AFTError

#######################################
# configurations
FS_NAME         = 'AeroFS'
FS_BIN          = 'aerofs.jar'
FLAG_NODM       = 'nodm'
FLAG_FS_LOG     = 'lol'
FILE_DAEMON_PID = 'pid'

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
    _aerofsPrograms = ['cli', 'daemon', 'sh', 'fsck']
    _bin = FS_BIN
    _procs = None
    
    def __init__(self, approot, fsroot, rtroot): 
        self._procs = []
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
        return join(self.getRTRoot(), 'daemon.log')
    def getGuiLog(self):
        return join(self.getRTRoot(), 'gui.log')

    def install(self): raise NotImplementedError

    # @param args:       a list of arguments to AeroFS, not java
    #
    def launch(self, args = []):
        # Set the flags to indicate lots of logging, and no daemon monitor
        with open(join(self.getRTRoot(), FLAG_NODM), 'a'): pass
        with open(join(self.getRTRoot(), FLAG_FS_LOG), 'a'): pass

        self._launchDaemon(args)
        self._launchCLI(args)
        
    # @param timeout:  permitted time in seconds to gracefully terminate
    #
    def terminate(self, timeout=5): 
        assert (len(self._procs) == 2) and all(self._procs)

        # Find any process that died early (has a return code)
        ps = filter(subprocess.Popen.poll, self._procs)
        for p in ps:
            raise AeroError(('pid {0} terminated early with code {1}'
                             ).format(p.pid, p.returncode))

        # Verify that the current daemon has same pid as the one launched
        try:
            with open(join(self.getRTRoot(), FILE_DAEMON_PID), 'r') as f:
                pid = int(f.read())
                if not any((p.pid == pid for p in self._procs)):
                    raise AeroError(
                            ('Current daemon process has different pid'
                              '{0}').format(pid))
        except IOError, e:
            raise AeroError(e) 
        except ValueError, e:
            raise AeroError('Could not convert pid to integer {0}'.format(e))

        for p in self._procs:
            p.terminate()
            tstart = time.time()
            while not p.poll():
                if time.time() - tstart > timeout:
                    self.kill()
                    raise AeroError(('{0} termination timeout over {1}s'
                                    ).format(self._bin, timeout))
                time.sleep(1)

            print 'terminated {1} {0}, with return code {2}'.format(
                    self._bin, p.pid, p.poll())
        
        # TODO should I verify anything else, e.g. log file?
        self._procs = []

    def kill(self): 
        try:
            for p in self._procs:
                p.kill()
        except OSError, data:
            print data
        self._procs = []

    #========================================================================
    # Helper methods
    def _launchDaemon(self, args):
        javaArgs = ['-ea', 
                        '-Xmx64m', 
                        '-XX:+UseConcMarkSweepGC',
                        '-Djava.net.preferIPv4Stack=true']
        self._launch('daemon', args, javaArgs)

    def _launchCLI(self, args):
        self._launch('cli', args)

    def _launch(self, program, args, javaArgs = []):
        assert program in self._aerofsPrograms

        cmd = ['java'] + javaArgs + \
              ['-jar',
               os.path.join(self.getAppRoot(), self._bin),
               'DEFAULT',
               program]
        cmd += args
        self._printCmd(cmd)
        try:
            self._procs.append(subprocess.Popen(cmd))
        except OSError, e:
            raise AeroError('When executing {1}, error {0}'.format(e,cmd))

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
    def launch(self, args = []):
        os.putenv('LD_LIBRARY_PATH', self._approot)
        AeroFS.launch(self, args)

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
    af.launch()
    time.sleep(5)
    #af.terminate()
    # Should fail with an assertion error
    af.terminate()
