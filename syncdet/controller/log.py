import sys, os

from os.path import join

import config, scn, lib, systems, case

def createLogFolders(verify):
    '''Create log folders on both the controller and actors. Although log
    folders on actors can be created lazily when needed, creating it here for
    all actors simplifies collectAllLogs() (as not all systems will be used for
    a scenario) and test cases.
    '''
    if verify: return

    # create the log folder regardless of whether logging is enabled, to ensure
    # scenario instances are unique
    pathCtrlrLogFolder = getControllerLogFolderPath()
    try:
        os.makedirs(pathCtrlrLogFolder)
    except OSError:
        if not os.path.exists(pathCtrlrLogFolder):
            print 'Directory ' + pathCtrlrLogFolder + ' could not be created';
            sys.exit();

    # create log directories on actor systems
    for system in systems.getSystems():
        path = getActorLogFolderPath(system)
        system.execRemoteCmdBlocking('mkdir -p ' + path)

def getLogFolderRelativePath():
    '''@return the log file path relative to SyncDET root folder'''
    return join(config.LOG_DIR, scn.getScenarioInstanceId());

def getControllerLogFolderPath():
    '''@return: the directory where the controller system stores log files
    locally
    '''
    return join(lib.getLocalRoot(), getLogFolderRelativePath());

def getControllerLogFilePath(sysId, module, instId):
    '''@return: the test case log path for the controller system'''
    name = case.getLogFileName(module, instId, sysId)
    return join(getControllerLogFolderPath(), name)

def getActorLogFolderPath(system):
    '''@return: the directory where the actor system stores log files
    '''
    return join(system.detRoot, getLogFolderRelativePath());

def getActorLogFilePath(system, sysId, module, instId):
    '''@return: the test case log path for the controller system'''
    name = case.getLogFileName(module, instId, sysId)
    return join(getActorLogFolderPath(system), name)

def collectLog(sysId, module, instId):
    '''Retrieve the log file of a specific test case instance from a given actor
    system to the local log directory
    '''

    pathCtrlr = getControllerLogFilePath(sysId, module, instId)
    system = systems.getSystem(sysId)
    pathActor = getActorLogFilePath(system, sysId, module, instId)
    system.copyFrom(pathActor, pathCtrlr)

def collectAllLogs():
    '''Retrieve all the log files under the log folders from all the actors to
    the local log directory
    '''

    for system in systems.getSystems():
        pathCtrlr = getControllerLogFolderPath()
        pathActor = getActorLogFolderPath(system)
        pathActor = os.path.join(pathActor, "*")

        system.copyFrom(pathActor, pathCtrlr)
