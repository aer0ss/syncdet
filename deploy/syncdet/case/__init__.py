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
def actor_id():
    global _actorId
    if not _actorId: _actorId = int(sys.argv[2])
    return _actorId

# return the number of actors that are running this case
# it is NOT the total number of actors
#
def actor_count():
    global _actorCount
    if not _actorCount: _actorCount = int(sys.argv[5])
    return _actorCount

# return the test case module name
#
def module_name():
    return sys.argv[1]

# return a unique instance ID of this test case
#
def instance_id():
    return sys.argv[4]

# return a unique instance ID of this scenario
# (e.g. date and time)
#
def scenario_id():
    return sys.argv[3]

# return any extra command line arguments passed to scn.execute()
# this is intended to be used as an internal tool for "under-the-hood" cases
# such as "tar_user_data"
#
def _extra_args():
    return sys.argv[6:]

# return any extra command line arguments passed to scn.execute()
# this is intended to be used by users in case files to access args that were
# specified during syncdet invocation:
#     ./syncdet.py [...] --case-arg=a1 --case-arg=a2 ...
#
def user_specified_args():
    return sys.argv[6:]

def instance_unique_string():
    """
    Return a string unique for every test case instance
    """
    return lib.instance_unique_string(module_name(), instance_id())

def instance_unique_hash32():
    """
    Return a 32 bit hash of the instance unique string
    Good for consistent seeding of PRNG across actors
    """
    return zlib.adler32(instance_unique_string())

def local_actor():
    """
    Return the actors.Actor object corresponding to this machine
    """
    if not actors.actor_list():
        actors.init(False, actor_count())
    return actors.actor(actor_id())

def root_path():
    """
    Return the SyncDET root on this local actor
    """
    return os.path.normpath(os.path.expanduser(local_actor().root))

def deployment_folder_path():
    """
    Return the deployment folder path on this local actor. SyncDET may remove
    this folder before or after running a scenario without notice.
    """
    return os.path.join(root_path(), param.DEPLOY_DIR)

def user_data_folder_path():
    """
    Return the user data folder path on this local actor. Test cases can use
    this folder to save arbitrary data. SyncDET or the actor's OS never removes
    this folder unless the user explicitly does so.
    """
    return os.path.join(root_path(), param.USER_DATA_DIR)

def log_folder_path():
    """
    Return the log folder path of the calling test case.
    Each scenario has a unique log folder path.
    """
    return lib.scenario_log_folder(root_path(), scenario_id())

def log_file_path(suffix = ''):
    """
    Return the log file path of the calling test case.
    Each test case instance has a unique log folder path.
    """
    return lib.scenario_log_file(log_folder_path(), module_name(),
                                 instance_id(), actor_id(), suffix)

def fail_test_case(msg = ""):
    """
    Call this method to fail a test case. An optional message can be provided
    to describe the failure. The message will be recorded in the test report.
    """
    print 'CASE_FAILED: {0}'.format(msg)
    sys.exit(1)
