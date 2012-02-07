import os, time

import case
from lib import *

def entry():
    luck = getUniquePath().__hash__() % case.getSysCount()
    if luck == case.getSysId():
        print 'put', getUniquePath()
        file = os.mkdir(getUniquePath())
        
        case.sync('barrier')
        
        os.rmdir(getUniquePath())

    else:
        print 'get', getUniquePath()
        waitDir(getUniquePath())
        
        case.sync('barrier')
        
        while 1:
            time.sleep(1)
            if not os.access(getUniquePath(), os.F_OK): break

spec = { 'default': entry }