import os, time
import case
import aerofsapp

#######################################
# configurations

# a general timeout value
WAIT_TIMEOUT    = 5

aeroApp = None #lib.createAeroFSApp()

#######################################
# lib functions

# Application directory (where aerofs.jar lives)
#
def getFSAppRoot(): pass

# Run Time directory (where databases and logs live)
#
def getFSRTRoot(): pass

# Directory where AeroFS stores/libraries are mounted
#
def getFSMountRoot(): pass

def launchFS(): pass
    
def terminateFS(ignoreError = False): pass

def killFS(): pass


# @param content     must be one line only
# @param mutable     true: return until the expected content appears
#                    false: raise a case.Failure if the file content is not
#                           empty and is not identical to what's expected
#
def waitFile(path, content, mutable = False):
    assert content
    while 1:
        time.sleep(1)
        if not os.access(path, os.F_OK): continue
    
        file = open(path, 'rb')
        line = file.readline()
        file.close()
        # the file might be initially empty when created
        if not line: continue
        if line != content:
            if mutable: continue
            else: raise case.Failure, 'string mismatch. expect "%s" ' \
                                'actual "%s" in file %s' % (str, line, path)
        break

def waitDir(path):
    while 1:
        time.sleep(1)
        if not os.access(path, os.F_OK): continue
        if not os.path.isdir(path):
            raise case.Failure, path + ' is not a directory'
        break
