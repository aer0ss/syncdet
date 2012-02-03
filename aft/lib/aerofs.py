import os.path, subprocess

#######################################
# configurations
FS_NAME         = 'AeroFS'


def createAeroFS(): pass #return AeroFSonLinux()

class AeroFSAbstact:
    _aerofsPrograms = ['cli', 'gui', 'daemon', 'sh', 'fsck']
    _proc = None

    def __init__(self): pass
    def getFSRoot(self): raise NotImplementedError 
    # Directory of AeroFS binaries
    def getAppRoot(self): raise NotImplementedError 
    # Directory of runtime data (db, logs, etc)
    def getRTRoot(self): raise NotImplementedError 
    def getDaemonLog(self): 
        return os.path.join(self.getRTRoot(), 'daemon.log')
    def getGuiLog(self):
        return os.path.join(self.getRTRoot(), 'gui.log')

    # args: a list of arguments
    #
    def launch(self, program, args = []):
        javaArgs = []
        if program == 'daemon':
            javaArgs += ['-ea', 
                        '-Xmx64m', 
                        '-XX:+UseConcMarkSweepGC',
                        '-Djava.net.preferIPv4Stack=true']
        self._launch(program, javaArgs, args)
        
    def terminate(self): raise NotImplementedError 
    def kill(self): raise NotImplementedError 
        # kill _pid

    def _launch(self, program, javaArgs, args):
        assert program in self._aerofsPrograms
        cmd = ['java'] + javaArgs + \
              ['-jar',
               os.path.join(self.getAppRoot(),'aerofs.jar'),
               'DEFAULT',
               program]
        cmd += args
        self._printCmd(cmd)
        _proc = subprocess.Popen(cmd)

        # TODO: verify safe/correct launch by looking at log files, 
        #       or communicating with daemon/shell

    def _printCmd(self, cmd): print ' '.join(cmd)

class AeroFSonLinux(AeroFSAbstact):
    def getFSRoot(self): return '~/AeroFS'
    def getAppRoot(self): return '~/.aerofs-bin'        
    def getRTRoot(self): return '~/.aerofs'

class AeroFSonLinuxStaging(AeroFSonLinux):
    def getRTRoot(self): return '~/.aerofs.staging'

class AeroFSonOSX(AeroFSAbstact):
    def getFSRoot(self): return '~/AeroFS'
    def getAppRoot(self): 
        return '/Applications/AeroFS.app/Contents/Resources/Java'
    def getRTRoot(self): return '~/Library/Caches/com.aerofs'

class AeroFSonOSXStaging(AeroFSonOSX):
    def getRTRoot(self): 
        return '~/Library/Caches/com.aerofs.staging'



