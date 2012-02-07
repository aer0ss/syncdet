import os, time

import case
from lib import *

def entry():
    if case.getSysCount() == 1: raise case.Failure, "must have 2 systems or more"
    
    p1 = getUniquePath().__hash__() % case.getSysCount()
    p2 = (p1 + 1) % case.getSysCount()
    str = 'update sys %d, move sys %d' % (p1, p2)
    if p1 == case.getSysId():
        print 'update', getUniquePath()
        file = open(getUniquePath(), 'wb')
        file.write(str)
        file.close()
        
        case.sync('offline', [p2])
        
        file = open(getUniquePath(), 'wb')
        file.write(str)
        file.close()
        
        waitFile(getUniquePath() + '.d/renamed', str)
        
    elif p2 == case.getSysId(): 
        print 'move', getUniquePath()
        waitFile(getUniquePath(), str)
        setOnline(False)
        
        case.sync('offline', [p1])
        
        os.mkdir(getUniquePath() + '.d')
        os.rename(getUniquePath(), getUniquePath() + '.d/renamed')
        setOnline(True)
        
    else:
        print 'get', getUniquePath()
        waitFile(getUniquePath() + '.d/renamed', str)
        
spec = { 'default': entry }