"""
This package contains modules that are available only to actors but not the
controller.
"""
import sys, os.path, zlib

from .. import actors, lib, param

OK = 0
FAIL = 1
TIMEOUT = 2

_actorId = None
_actorCount = None

# return the Actor ID of this local actor
# (actor IDs form a total order)
#
def getActorId():
    global _actorId
    if not _actorId: _actorId = int(sys.argv[2])
    return _actorId

# return the number of actors that are running this case
# it is NOT the total number of actors
#
def getActorCount():
    global _actorCount
    if not _actorCount: _actorCount = int(sys.argv[5])
    return _actorCount

# return the test case module name
#
def getModuleName():
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

def getInstanceUniqueString():
    """
    Return a string unique for every test case instance
    """
    return lib.instance_unique_string(getModuleName(), getInstanceId())

def instance_unique_hash32():
    """
    Return a 32 bit hash of the instance unique string
    Good for consistent seeding of PRNG across actors
    """
    return zlib.adler32(getInstanceUniqueString())

def getLocalActor():
    """
    Return the actors.Actor object corresponding to this machine
    """
    if not actors.getActors():
        actors.init(False, getActorCount())
    return actors.getActor(getActorId())

def root_path():
    """
    Return the SyncDET root on this local actor
    """
    return os.path.normpath(os.path.expanduser(getLocalActor().root))

def getDeploymentFolderPath():
    """
    Return the deployment folder path on this local actor. SyncDET may remove
    this folder before or after running a scenario without notice.
    """
    return os.path.join(root_path(), param.DEPLOY_DIR)

def getUserDataFolderPath():
    """
    Return the user data folder path on this local actor. Test cases can use
    this folder to save arbitrary data. SyncDET or the actor's OS never removes
    this folder unless the user explicitly does so.
    """
    return os.path.join(root_path(), param.USER_DATA_DIR)

def getLogFolderPath():
    """
    Return the log folder path of the calling test case.
    Each scenario has a unique log folder path.
    """
    return lib.scenario_log_folder(root_path(), getScenarioId())

def getLogFilePath(suffix = ''):
    """
    Return the log file path of the calling test case.
    Each test case instance has a unique log folder path.
    """
    return lib.scenario_log_file(getLogFolderPath(), getModuleName(),
            getInstanceId(), getActorId(), suffix)

def failTestCase(msg = ""):
    """
    Call this method to fail a test case. An optional message can be provided
    to describe the failure. The message will be recorded in the test report.
    """
    print 'CASE_FAILED: {0}'.format(msg)
    sys.exit()
