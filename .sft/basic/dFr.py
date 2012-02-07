import os, time

import case
from lib import *

def entry():
    luck = getUniquePath().__hash__() % case.getSysCount()
    str = 'written by sys %d' % luck
    if luck == case.getSysId():
        print 'put', getUniquePath()
        file = open(getUniquePath(), 'wb')
        file.write(str)
        file.close()
        
        case.sync('barrier')
        
        os.remove(getUniquePath())

    else:
        print 'get', getUniquePath()
        waitFile(getUniquePath(), str)
        
        case.sync('barrier')
        
        while 1:
            time.sleep(1)
            if not os.access(getUniquePath(), os.F_OK): break

spec = { 'default': entry }