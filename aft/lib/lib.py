import os, time, os.path
import case
import aerofsapp, file

#######################################
# configurations

# a general timeout value
WAIT_TIMEOUT    = 5

aeroApp = None #lib.createAeroFSApp()

#######################################
# lib functions
def init(seed = None):
    file.init(seed)

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



# @param root        the directory containing the tree to be created
# @param depth       0: make files in root, with no subdirectories
#                    1: make files in root, with one more level of subdirs
# @param nsubdirs    number of subdirectories for each directory
# @param nfiles      number of files per directory
# @param maxfilesize maximum file size, in bytes
#
def makeDirTree(root, depth, nsubdirs = 1, nfiles = 1, maxfilesize = 8): 
    return file.makeDirTree(root, depth, nsubdirs, nfiles, maxfilesize)



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
