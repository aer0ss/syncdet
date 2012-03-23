import sys, os.path, datetime, time

import systems

s_realRoot = os.path.realpath(os.path.expanduser(sys.path[0]))

def getLocalRoot(): return s_realRoot

def getSysCount():
    assert len(systems.systems) > 0
    return len(systems.systems)
    #global s_sysCount
    #return s_sysCount


def generateTimeDerivedId(includeMSec):
    '''Generate a string based on the current time. the string can be used as
    identifier of test executions, etc
    '''
    now = datetime.datetime.today()
    ret = '%d.%02d.%02d.%02d%02d%02d' % (now.year, now.month, now.day,
                                            now.hour, now.minute, now.second)
    if includeMSec:
        ret += '.' + str(int(round(time.time() * 1000)) % 1000)

    return ret
