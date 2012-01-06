import sys, os, os.path

import systems, config

OK        = 0
FAIL      = 1
TIMEOUT   = 2

class Failure(RuntimeError): pass

s_sysId = None
s_sysCount = None

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

def getCaseModuleName():
    return sys.argv[1]

def getInstanceId():
    return sys.argv[4]

def getScenarioId():
    return sys.argv[3]

def getControllerRoot():
    return sys.argv[7]
    
def getSystem(sysId):
    return systems.systems[sysId]

def getSystemAddress(sysId):
    return getSystem(sysId)['address']

def getLocalSystem():
    return systems.systems[getSysId()]

def copyFrom(sysId, src, dst):
    str = getSystem(sysId)['copyFrom']
    str = str.replace('%host', getSystemAddress(sysId))
    str = str.replace('%src', src)
    str = str.replace('%dst', dst)
    print str
    os.system(str)

def copyTo(src, sysId, dst):
    str = getSystem(sysId)['copyTo']
    str = str.replace('%host', getSystemAddress(sysId))
    str = str.replace('%src', src)
    str = str.replace('%dst', dst)
    print str
    os.system(str)

def getLocalRoot(): return getLocalSystem()['detRoot']

def getLogDir():
    return '%s/%s/%s' % (getLocalRoot(),
                         config.LOG_DIR, 
                         getScenarioId())

def getControllerLogDir():
    return '%s/%s/%s' % (getControllerRoot(),
                         config.LOG_DIR, 
                         getScenarioId())
    
def getLogFilePath():
    return os.path.join(getLogDir(),
                        '%s.%s.%s' % (getCaseModuleName(),
                                      getInstanceId(),
                                      getSysId()))

