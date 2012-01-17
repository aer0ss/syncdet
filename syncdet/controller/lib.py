import sys, os.path

import systems

s_realRoot = os.path.realpath(os.path.expanduser(sys.path[0]))

def getLocalRoot(): return s_realRoot

def getSysCount(): 
    assert len(systems.systems) > 0
    return len(systems.systems)
    #global s_sysCount
    #return s_sysCount
