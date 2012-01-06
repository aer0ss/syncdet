import os

import case
import lib

def entry():
    cmd = 'rm -rf %s' % lib.getLocalFSRoot()
    print cmd
    os.system(cmd)

spec = { 'default': entry }