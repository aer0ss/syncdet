import sys, os

import config, scn, lib

from case import getLogFileName

# static initialization
#
s_localLogDir = '{0}/{1}/{2}'.format(lib.getLocalRoot(), config.LOG_DIR,
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

def getLocalLogPath(sysId, module, instId):
    '''@return: the test case log path for the controller system'''
    return os.path.realpath(os.path.join(getLocalLogDir(),
            getLogFileName(module, instId, sysId)))

def getLocalLogDir():
    '''@return: the test case log directory for the controller system'''
    global s_localLogDir
    return s_localLogDir
