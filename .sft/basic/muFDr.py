import os, time
import case
from lib import *

# create a unique dir 'uniquepath.child'
# create a file in it
# move the file in and out the dir and at the same time change the file name
#     and its content
# move the directory around, and create a second dir 'uniquepath.parent'
# finally move the the child into the parent
# 

MAX_MOVES = 100

def entry():
    luck   = getUniquePath().__hash__() % case.getSysCount()
    moves  = 1 + (getUniquePath().__hash__() % MAX_MOVES)
    # make the move even
    moves += moves % 2
    finalpath = '%s.parent/child.%d/file.%d' % (getUniquePath(),
                                                   moves - 1, moves - 1)
    finalstr  = 'written by %d update %d' % (luck, moves - 1)
    
    if luck == case.getSysId():
        print 'put', finalpath, moves, 'moves'
        curchild = getUniquePath() + '.child.-1'
        curstr = 'written by %d update %d' % (luck, -1)
        curpath  = curchild + '/file.-1'
        os.mkdir(curchild)
        file = open(curpath, 'wb')
        file.write(curstr)
        file.close()
        
        # move the file around and update
        for i in xrange(moves):
            if i % 2: newpath = curchild + '/file.' + str(i)
            else: newpath = getUniquePath() + '.file.' + str(i)
            os.rename(curpath, newpath)
            curpath = newpath
            
            curstr = 'written by %d update %d' % (luck, i)
            file = open(curpath, 'wb')
            file.write(curstr)
            file.close()
            
        assert curpath == curchild + '/file.' + str(moves - 1)
            
        # move the directory and the file around
        parent = '%s.parent' % getUniquePath()
        os.mkdir(parent)
        first = True
        for i in xrange(moves):
            if i % 2: newchild = parent + '/child.' + str(i)
            else: newchild = getUniquePath() + '.child.' + str(i)
            os.rename(curchild, newchild)
            curchild = newchild
            
            if first:
                curpath = getUniquePath() + '.child.0/file.' + str(moves - 1)                
                first = False
            else:
                curpath = curchild + '/file.' + str(i - 1)
            newpath = curchild + '/file.' + str(i)
            os.rename(curpath, newpath)
            curpath = newpath
        assert curpath == finalpath
        
    else:
        print 'get', finalpath
        waitFile(finalpath, finalstr, True)

spec = { 'default': entry }