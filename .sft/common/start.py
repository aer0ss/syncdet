import os

import lib

def entry():
    lib.launchFS()
    return 'fs log at ' + lib.getControllerFSLogFilePath()
    
spec = { 'default': entry }