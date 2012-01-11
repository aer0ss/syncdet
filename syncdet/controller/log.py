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

# make the log path for the controller system
#
def getLocalLogPath(sysId, module, instId):
    global s_localLogDir
    return '%s/%s.%s.%s' % (s_localLogDir, module, instId, sysId)
