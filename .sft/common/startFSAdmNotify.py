import os

from lib import *

def entry():
    mnt = getLocalMountPoint()
    launchFSAdmDaemon(['notify', mnt, '1'])
    return 'fsadm log at ' + getControllerFSAdmDaemonLogFilePath()
    
spec = { 'default': entry }