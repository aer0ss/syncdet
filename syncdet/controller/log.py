import sys, os

import config, scn, lib

# static initialization
#
s_localLogDir = '%s/%s/%s' % (lib.getLocalRoot(), config.LOG_DIR, 
                       scn.getScenarioInstanceId())

# create the dir regardless of whether logging is enabled, to ensure scenario
# instances are unique
try:
    os.makedirs(s_localLogDir)
except OSError:
    if not os.path.exists(s_localLogDir):
        print 'Directory ' + s_localLogDir + ' could not be created';
        sys.exit();

if config.DIRECTORY_SHARING and config.MAKE_SHARED_DIRECTORY_WRITABLE:
    os.system(config.MAKE_SHARED_DIRECTORY_WRITABLE % s_localLogDir)

# Return the log file path, relative to the log directory
#
def getRelativeLogPath(sysId, module, instId):
    return '%s.%s.%s' % (module, instId, sysId)

# make the log path for the controller system
#
def getLocalLogPath(sysId, module, instId):
    global s_localLogDir
    return os.path.realpath(os.path.join(
                s_localLogDir, getRelativeLogPath(sysId, module, instId)))
