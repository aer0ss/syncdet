import os, time
import case
from lib import *

MAX_DEPTH = 50
MAX_MOVES = 49

def entry():
    depth = getUniquePath().__hash__() % MAX_DEPTH
    moves = getUniquePath().__hash__() % MAX_MOVES
    luck = getUniquePath().__hash__() % case.getSysCount()
    dir  = getUniquePath() + '.%d' % luck

    if luck == case.getSysId():
        print 'put', dir, 'depth', depth, 'moves', moves
        
        # create 'em
        path = dir
        os.mkdir(path)
        for i in xrange(depth):
            path = path + '/%d.%d' % (i, -1)
            os.mkdir(path)
            # create a dumb file in each dir
            file = open(path + '/dumb', 'wb')
            file.write(path)
            file.close()
            
        # move 'em
        for j in xrange(moves):
            path = dir
            for i in xrange(depth):
                old = '%s/%d.%d' % (path, i, j - 1)
                new = '%s/%d.%d' % (path, i, j)
                os.rename(old, new)
                path = new
                time.sleep(0.1)
            
    else:
        print 'get', dir
        for i in xrange(depth):
            dir = dir + '/%d.%d' % (i, moves - 1)

        waitDir(dir)


spec = { 'default': entry }