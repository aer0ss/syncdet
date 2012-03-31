import sys, os
import scn, actors
from controller_lib import getRootPath
from syncdet_lib import getLogFolderPath, getLogFilePath

def createLogFolders(verify):
    '''Create log folders on both the controller and actors. Although log
    folders on actors can be created lazily when needed, creating it here for
    all actors simplifies collectAllLogs() (as not all actors will be used for
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

    # create log directories on actor actors
    for actor in actors.getActors():
        path = getActorLogFolderPath(actor)
        actor.execRemoteCmdBlocking('mkdir -p ' + path)


def getControllerLogFolderPath():
    '''@return: the directory where the controller actor stores log files
    locally'''
    return getLogFolderPath(getRootPath(), scn.getScenarioId());

def getControllerLogFilePath(actorId, module, instId):
    '''@return: the test case log path for the controller actor'''
    return getLogFilePath(getControllerLogFolderPath(), module, instId, actorId)

def getActorLogFolderPath(actor):
    '''@return: the directory where the actor actor stores log files
    '''
    return getLogFolderPath(actor.root, scn.getScenarioId());

def getActorLogFilePath(actor, actorId, module, instId):
    '''@return: the test case log path for the controller actor'''
    return getLogFilePath(getActorLogFolderPath(actor), module, instId, actorId)

def collectLog(actorId, module, instId):
    '''Retrieve the log file of a specific test case instance from a given actor
    actor to the local log directory
    '''

    pathCtrlr = getControllerLogFilePath(actorId, module, instId)
    actor = actors.getActor(actorId)
    pathActor = getActorLogFilePath(actor, actorId, module, instId)
    actor.copyFrom(pathActor, pathCtrlr)

def collectAllLogs():
    '''Retrieve all the log files under the log folders from all the actors to
    the local log directory
    '''

    for actor in actors.getActors():
        pathCtrlr = getControllerLogFolderPath()
        pathActor = getActorLogFolderPath(actor)
        pathActor = os.path.join(pathActor, "*")

        actor.copyFrom(pathActor, pathCtrlr)
