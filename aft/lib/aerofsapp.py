import os.path

#######################################
# configurations
FS_NAME         = 'AeroFS'


def createAeroFSApp(): pass #return AeroFSAppLinux()

class AeroFSApp:
    def __init__(self): pass
    # Directory of AeroFS binaries
    def getAppRoot(self): pass
    # Directory of runtime data (db, logs, etc)
    def getRTRoot(self): pass
    def getFSRoot(self): pass
    def getDaemonLog(self): 
        return os.path.join(self.getRTRoot(), 'daemon.log')
    def getGuiLog(self):
        return os.path.join(self.getRTRoot(), 'gui.log')

    # args: a list of arguments
    #
    def launch(self, args = []): pass
    def terminate(self): pass

#class AeroFSAppLinux(AeroFSApp):
#    def __init__(self): pass
#    def getAppRoot(self): 
        
