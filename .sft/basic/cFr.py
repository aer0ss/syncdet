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
    else: 
        print 'get', getUniquePath()
        waitFile(getUniquePath(), str)

spec = { 'default': entry }