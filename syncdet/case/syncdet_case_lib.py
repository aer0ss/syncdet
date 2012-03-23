import sys, os.path

import config, systems

OK = 0
FAIL = 1
TIMEOUT = 2

s_sysId = None
s_sysCount = None

# return the System ID of this local system
# (system IDs form a total order)
#
def getSysId():
    global s_sysId
    if not s_sysId: s_sysId = int(sys.argv[2])
    return s_sysId

# return the number of systems that are running this case
# it is NOT the total number of systems
#
def getSysCount():
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

# return the SyncDET root on the controller system
#
def getControllerRoot():
    return sys.argv[7]

# return a reference to instance of systems.System for this machine
#
def getLocalSystem():
    if not systems.systems:
        systems.init(False, getSysCount())
    return systems.getSystem(getSysId())

# return the SyncDET root on this local system
#
def getLocalRoot(): return getLocalSystem().detRoot

def getLogDir():
    return '%s/%s/%s' % (getLocalRoot(),
                         config.LOG_DIR,
                         getScenarioId())

def getControllerLogDir():
    return '%s/%s/%s' % (getControllerRoot(),
                         config.LOG_DIR,
                         getScenarioId())

def getLogFileName(module, instId, sysId, suffix = ''):
    '''Return the log file name'''
    return '{0}-{1}-{2}{3}.log'.format(module, instId, sysId, suffix)

def getLogFilePath(suffix = ''):
    '''Return the log file path of the calling test case'''
    name = getLogFileName(getCaseModuleName(), getInstanceId(), getSysId(),
            suffix)
    return os.path.normpath(os.path.expanduser(os.path.join(getLogDir(), name)))

# Call this method to fail a test case. An optional message can be provided
# to describe the failure 
def failTestCase(msg = ""):
    print 'CASE_FAILED: {0}'.format(msg)
    sys.exit()
