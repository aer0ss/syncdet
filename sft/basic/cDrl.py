import os, time

import case
from lib import *

MAX_DEPTH = 300

def entry():
    depth = getUniquePath().__hash__() % MAX_DEPTH
    luck = getUniquePath().__hash__() % case.getSysCount()
    dir  = getUniquePath() + '.%d' % luck

    if luck == case.getSysId():
        print 'put', dir, 'depth', depth
        os.mkdir(dir)
        for i in xrange(depth):
            dir = dir + '/%d' % i
            os.mkdir(dir)
            #time.sleep(0.1)
        
    else:
        print 'get', dir
        for i in xrange(depth):
            dir = dir + '/%d' % i

        waitDir(dir)


spec = { 'default': entry }