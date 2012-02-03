import os.path, subprocess

#######################################
# configurations
FS_NAME         = 'AeroFS'


def createAeroFSApp(): pass #return AeroFSAppLinux()

class AeroFSApp:
    _aerofsPrograms = ['cli, gui, daemon, sh, fsck']
    _proc = None

    def __init__(self): pass
    # Directory of AeroFS binaries
    def getAppRoot(self): raise NotImplementedError 
    # Directory of runtime data (db, logs, etc)
    def getRTRoot(self): raise NotImplementedError 
    def getFSRoot(self): raise NotImplementedError 
    def getDaemonLog(self): 
        return os.path.join(self.getRTRoot(), 'daemon.log')
    def getGuiLog(self):
        return os.path.join(self.getRTRoot(), 'gui.log')

    # args: a list of arguments
    #
    def launch(self, program, args = []):
        assert program in _aerofsPrograms
        cmd = ['java', '-jar',
               os.path.join(self.getAppRoot(),'aerofs.jar'),
               'DEFAULT',
               program]
        cmd += args
        self._printCmd(cmd)
        _proc = subprocess.Popen(cmd)

        # TODO: verify safe/correct launch by looking at log files, 
        #       or communicating with daemon/shell
        
    def terminate(self): raise NotImplementedError 
    def kill(self): raise NotImplementedError 
        # kill _pid

    def _printCmd(cmd): print ' '.join(cmd)

class AeroFSAppLinux(AeroFSApp):
    def getAppRoot(self): return '~/.aerofs-bin'        
    def getFSRoot(self): return '~/AeroFS'

class AeroFSAppLinuxProd(AeroFSAppLinux):
    def getRTRoot(self): return '~/.aerofs'

class AeroFSAppLinuxStaging(AeroFSAppLinux):
    def getRTRoot(self): return '~/.aerofs.staging'

class AeroFSAppOSX(AeroFSApp):
    def getAppRoot(self): 
        return '/Applications/AeroFS.app/Contents/Resources/Java'
    def getFSRoot(self): return '~/AeroFS'

class AeroFSAppOSXProd(AeroFSAppOSX):
    def getRTRoot(self): 
        return '~/Library/Caches/com.aerofs'

class AeroFSAppOSXStaging(AeroFSAppOSX):
    def getRTRoot(self): 
        return '~/Library/Caches/com.aerofs.staging'
