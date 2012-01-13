import sys, os.path

import systems

s_realRoot = os.path.realpath(os.path.expanduser(sys.path[0]))

def getLocalRoot(): return s_realRoot

s_sysCount = len(systems.systems)

def getSysCount(): 
    global s_sysCount
    return s_sysCount

def setSysCount(cnt): 
    global s_sysCount
    s_sysCount = min(cnt, len(systems.systems))
