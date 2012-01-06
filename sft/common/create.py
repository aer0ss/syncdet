import time, os

import case
import lib


def createFounder():
    lib.launchFSAdm(['create', '-f'])
    
    args = []
    for i in range(1, case.getSysCount()):
        args += ['-i', case.getSystemAddress(i)]
    
    lib.launchFS(args)
    lib.terminateFS()

def createOthers():
    case.copyFrom(0, lib.getFSRoot(0), lib.getLocalFSRoot())
    if not os.access(lib.getLocalFSRoot(), os.F_OK):
        raise case.Failure, 'failed to copy over ' + lib.getLocalFSRoot()
    lib.launchFSAdm(['create'])
    
def entry():
    try:
        case.syncPrev('create')
        if case.getSysId() == 0: createFounder()
        else: createOthers()
    finally:
        case.syncNext('create')
    
spec = { 'default': entry }