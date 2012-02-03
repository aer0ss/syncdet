import os, time, os.path, random
import case
import aerofs, file

#######################################
# configurations

# a general timeout value
WAIT_TIMEOUT    = 5

aero = aerofs.createAeroFS()

#######################################
# lib functions
def init(seed = None):
    # Set the random seed here, one common place, in case many modules use it
    random.seed(seed)
    #file.init(seed)

# Application directory (where aerofs.jar lives)
#
def getFSAppRoot(): return aero.getAppRoot()

# Run Time directory (where databases and logs live)
#
def getFSRTRoot(): return aero.getRTRoot()

# Directory where AeroFS stores/libraries are mounted
#
def getFSMountRoot(): return aero.getFSRoot()

def launchFS(program = 'daemon'): aero.launch(program)
def launchFSDaemon(): aero.launch('daemon')

def terminateFS(ignoreError = False): aero.terminate()

def killFS(): aero.kill()


# @param subsets     tuple of subsets of peers that can intra-communicate
#
def networkPartition(subsets): pass
def clearNetworkPartition(): pass

# @param root        the directory to be the root of the tree
# @param depth       0: make files in root, with no subdirectories
#                    1: make files in root, with one more level of subdirs
# @param nsubdirs    number of subdirectories for each directory
# @param nfiles      number of files per directory
# @param maxfilesize maximum file size, in bytes
#
def makeDirTree(root, depth, nsubdirs, nfiles, maxfilesize = 100): 
    return file.makeDirTree(dpath, depth, nsubdirs, nfiles, maxfilesize)



# @param content     must be one line only
# @param mutable     true: return until the expected content appears
#                    false: raise a case.Failure if the file content is not
#                           empty and is not identical to what's expected
#
def waitFile(path, content, mutable = False):
    pass

def waitDir(path): 
    while 1:
        time.sleep(1)
        if not os.path.exists(path): continue
        if not os.path.isdir(path):
            raise case.Failure, path + ' is not a directory'
        break

def waitDirTree(root, depth, nsubdirs, nfiles): pass
