import sys, os

import config, scn, lib, systems

from case import getLogFileName

def initialize(verify):
    if verify: return

    # create the log folder regardless of whether logging is enabled, to ensure 
    # scenario instances are unique
    localLogDir = getLocalLogFolderPath()
    try:
        os.makedirs(localLogDir)
    except OSError:
        if not os.path.exists(localLogDir):
            print 'Directory ' + localLogDir + ' could not be created';
            sys.exit();

    # create log directories on actor systems
    for system in systems.getSystems():
        path = localToActorPath(localLogDir, system)
        system.execRemoteCmdBlock('mkdir -p ' + path)

def getLocalLogFolderPath():
    '''@return: the directory where the controller system stores log files
    locally
    '''
    return '{0}/{1}/{2}'.format(lib.getLocalRoot(), config.LOG_DIR,
                       scn.getScenarioInstanceId());

def getLocalLogPath(sysId, module, instId):
    '''@return: the test case log path for the controller system'''
    return os.path.realpath(os.path.join(getLocalLogFolderPath(),
            getLogFileName(module, instId, sysId)))

def localToActorPath(path, system):
    # The remote file name should be the same, needing only account for
    # a different SyncDET root
    return path.replace(lib.getLocalRoot(), system.detRoot)

def collectLog(sysId, module, instId):
    '''Retrieve the log file of a specific test case instance from a given actor
    system to the local log directory
    '''

    # Determine where the logfile should be stored locally
    localLogPath = getLocalLogPath(sysId, module, instId)

    system = systems.getSystem(sysId)
    system.copyFrom(localToActorPath(localLogPath, system), localLogPath)

def collectAllLogs():
    '''Retrieve all the log files under the log folders from all the actors to
    the local log directory
    '''

    for system in systems.getSystems():
        # Determine where the log file should be stored locally
        localLogDir = getLocalLogFolderPath()

        remLogPath = localToActorPath(localLogDir, system)
        remLogPath = os.path.join(remLogPath, "*")

        system.copyFrom(remLogPath, localLogDir)
