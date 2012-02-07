import os, time

import case
from lib import *

def entry():
    luck = getUniquePath().__hash__() % case.getSysCount()
    dir = getUniquePath() + '.%d' % luck
    if luck == case.getSysId():
        print 'put', dir
        os.mkdir(dir)        
    else:
        print 'get', dir
        waitDir(dir)


spec = { 'default': entry }