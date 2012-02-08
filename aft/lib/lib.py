import os, time, os.path, random
import case
import aerofs, file

#######################################
# configurations
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

# Launch AeroFS daemon and cli 
# (but CLI will not restart daemon on crash)
#
def launchFS(args = []): aero.launch(args)

# Launch AeroFS daemon only
#
def launchFSDaemon(args = []): aero._launchDaemon(args)

# Gracefully terminate AeroFS processes launched by this library
#
def terminateFS(ignoreError = False): aero.terminate()

# Kill AeroFS processes launched by this library
#
def killFS(): aero.kill()


# @param subsets     tuple of subsets of peers that can intra-communicate
#
def networkPartition(subsets): raise NotImplementedError
def clearNetworkPartition(): raise NotImplementedError

# @param root        the directory to be the root of the tree
# @param depth       0: make files in root, with no subdirectories
#                    1: make files in root, with one more level of subdirs
# @param nsubdirs    number of subdirectories for each directory
# @param nfiles      number of files per directory
# @param maxfilesize maximum file size, in bytes
#
def makeDirTree(root, depth, nsubdirs, nfiles, maxfilesize = 100): 
    return file.makeDirTree(dpath, depth, nsubdirs, nfiles, maxfilesize)


#######################################################################
# The following are experimental and not currently part of the API

# @param content     must be one line only
# @param mutable     true: return until the expected content appears
#                    false: raise a case.Failure if the file content is not
#                           empty and is not identical to what's expected
#
#def waitFile(path, content, mutable = False):
#    pass
#
#def waitDir(path): 
#    while 1:
#        time.sleep(1)
#        if not os.path.exists(path): continue
#        if not os.path.isdir(path):
#            raise case.Failure, path + ' is not a directory'
#        break
#
#def waitDirTree(root, depth, nsubdirs, nfiles): pass
