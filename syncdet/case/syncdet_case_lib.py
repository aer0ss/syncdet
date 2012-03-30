import sys, os.path

import actors, syncdet_lib

OK = 0
FAIL = 1
TIMEOUT = 2

s_actorId = None
s_actorCount = None

# return the Actor ID of this local actor
# (actor IDs form a total order)
#
def getActorId():
    global s_actorId
    if not s_actorId: s_actorId = int(sys.argv[2])
    return s_actorId

# return the number of actors that are running this case
# it is NOT the total number of actors
#
def getActorCount():
    global s_actorCount
    if not s_actorCount: s_actorCount = int(sys.argv[5])
    return s_actorCount

# return the test case module name
#
def getCaseModuleName():
    return sys.argv[1]

# return a unique instance ID of this test case
#
def getInstanceId():
    return sys.argv[4]

# return a unique instance ID of this scenario
# (e.g. date and time)
#
def getScenarioId():
    return sys.argv[3]

# return a reference to instance of actors.Actor for this machine
#
def getLocalActor():
    if not actors.actors:
        actors.init(False, getActorCount())
    return actors.getActor(getActorId())

# return the SyncDET root on this local actor
#
def getRootFolderPath():
    return os.path.normpath(os.path.expanduser(getLocalActor().detRoot))

def getLogFolderPath():
    '''Return the log folder path of the calling test case.
    Each scenario has a unique log folder path.'''
    return syncdet_lib.getLogFolderPath(getRootFolderPath(), getScenarioId())

def getLogFilePath(suffix = ''):
    '''Return the log file path of the calling test case.
    Each test case instance has a unique log folder path.'''
    return syncdet_lib.getLogFilePath(getLogFolderPath(), getCaseModuleName(),
            getInstanceId(), getActorId(), suffix)

def failTestCase(msg = ""):
    '''Call this method to fail a test case. An optional message can be provided
    to describe the failure. The message will be recorded in the test report.
    '''
    print 'CASE_FAILED: {0}'.format(msg)
    sys.exit()
