import sys, os.path

import systems, syncdet_lib

OK = 0
FAIL = 1
TIMEOUT = 2

s_sysId = None
s_sysCount = None

# return the System ID of this local system
# (system IDs form a total order)
#
def getSystemId():
    global s_sysId
    if not s_sysId: s_sysId = int(sys.argv[2])
    return s_sysId

# return the number of systems that are running this case
# it is NOT the total number of systems
#
def getSystemCount():
    global s_sysCount
    if not s_sysCount: s_sysCount = int(sys.argv[5])
    return s_sysCount

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

# return a reference to instance of systems.System for this machine
#
def getLocalSystem():
    if not systems.systems:
        systems.init(False, getSystemCount())
    return systems.getSystem(getSystemId())

# return the SyncDET root on this local system
#
def getRootFolderPath():
    return os.path.normpath(os.path.expanduser(getLocalSystem().detRoot))

def getLogFolderPath():
    '''Return the log folder path of the calling test case.
    Each scenario has a unique log folder path.'''
    return syncdet_lib.getLogFolderPath(getRootFolderPath(), getScenarioId())

def getLogFilePath(suffix = ''):
    '''Return the log file path of the calling test case.
    Each test case instance has a unique log folder path.'''
    return syncdet_lib.getLogFilePath(getLogFolderPath(), getCaseModuleName(),
            getInstanceId(), getSystemId(), suffix)

def failTestCase(msg = ""):
    '''Call this method to fail a test case. An optional message can be provided
    to describe the failure. The message will be recorded in the test report.
    '''
    print 'CASE_FAILED: {0}'.format(msg)
    sys.exit()
