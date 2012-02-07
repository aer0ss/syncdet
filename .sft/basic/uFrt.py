import os, time

import case
from lib import *

MAX_UPDATES = 300

def entry():
    luck = getUniquePath().__hash__() % case.getSysCount()
    updates = 1 + (getUniquePath().__hash__() % MAX_UPDATES)
    if luck == case.getSysId():
        print 'put', getUniquePath(), updates, 'updates'
        for i in xrange(updates):
            str = 'written by %d update %d' % (luck, i)
            file = open(getUniquePath(), 'wb')
            file.write(str)
            file.close()
            time.sleep(0.1)
    else: 
        print 'get', getUniquePath()
        str = 'written by %d update %d' % (luck, updates - 1)
        waitFile(getUniquePath(), str, True)

spec = { 'default': entry }