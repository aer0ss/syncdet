import os, sys, signal, time, os.path

import case

#######################################
# configurations

FS_NAME         = 'SyncFS'
FS_UNIX_NAME    = 'syncfs'
FS_PROG_NAME    = 'fs'
FSADM_NAME      = 'SyncFS Admin'
FSADM_UNIX_NAME = 'fsadm'
FSADM_PROG_NAME = 'fsadm'

FS_PID_FILE_PATH = '/var/run/' + FS_UNIX_NAME + '.pid'

# a general timeout value
WAIT_TIMEOUT    = 5

#######################################
# lib functions

def getFSBinRoot(sysId): return case.getSystem(sysId)['syncfs.bin']

def getLocalFSBinRoot(): return case.getLocalSystem()['syncfs.bin']

def getFSRoot(sysId): return case.getSystem(sysId)['syncfs.root']

def getLocalFSRoot(): return case.getLocalSystem()['syncfs.root']

def getMountPoint(sysId): return case.getSystem(sysId)['syncfs.mnt']

def getLocalMountPoint(): return case.getLocalSystem()['syncfs.mnt']

def getFSLogBaseName():
    return '%s.%d' % (FS_UNIX_NAME, case.getSysId())

def getFSLogFilePath():
    return os.path.join(case.getLogDir(), getFSLogBaseName())

def getControllerFSLogFilePath():
    return os.path.join(case.getControllerLogDir(), getFSLogBaseName())

def getUniqueString():
    return '%s.%s' % (case.getCaseModuleName(), case.getInstanceId())

def getUniquePath():
    return os.path.join(getLocalMountPoint(), getUniqueString())

# return the line number of the occurence. 0 if not found or the file doesnt'
# exist
#
def timedSearchFSLogFile(path, string, timeout = WAIT_TIMEOUT):
    DELAY = 0.3
    retry = 0
    while 1:
        if os.access(path, os.F_OK):
            file = open(path, 'rb')
            lno = 0
            while 1:
                line = file.readline()
                if not line:
                    lno = 0
                    break
                lno += 1
                if line.find(string) != -1: break
            file.close()
            if lno: return lno
        retry += 1
        if retry >= timeout / DELAY: return 0
        time.sleep(DELAY)
            
def printCmd(cmd):
    for i in cmd: print i,
    print
    
def getLogPathFilePath():
    return '/tmp/synclog'

# args: a list of arguments
#
def launchFS(args = []):
    cmd = ['%s/%s' % (getLocalFSBinRoot(), FS_PROG_NAME),
           '-l', getFSLogFilePath(),
           '-q',
           getLocalMountPoint()]
    cmd += args
    printCmd(cmd)
    os.spawnv(os.P_WAIT, cmd[0], cmd)

    # wait for stabilization
    if not timedSearchFSLogFile(getFSLogFilePath(), FS_NAME + ' launched'):
        raise case.Failure, 'failed to launch fs. see fs log '\
                             + getControllerFSLogFilePath()

    # write the location of the log file (for termination from another 
    # scenario instance)
    file = open(getLogPathFilePath(), 'wb')
    file.write(getFSLogFilePath() + '\n')
    file.close()

def terminateFS(ignoreError = False):
    # umount first
    cmd = ['umount', getLocalMountPoint()]
    printCmd(cmd)
    os.spawnvp(os.P_WAIT, cmd[0], cmd)

    try:
        # find the logfile path
        file = open(getLogPathFilePath(), 'rb')
        path = file.readline()
        path = path[:-1]
        file.close()
    except IOError:
        if not ignoreError:
            raise case.Failure, "fs hasn't been running"
        else:
            return

    # remove the log path file
    os.remove(getLogPathFilePath())
    
    # waiting for the signature to apprear
    if timedSearchFSLogFile(path, FS_NAME + ' terminated'): return

    # forcedly terminate
    killFS()
    if not ignoreError:
        raise case.Failure,  'fs terminated abnormally. see '\
                     + path[len(case.getLocalRoot()) + 1:]

def killFS():
    try:
        file = open(FS_PID_FILE_PATH, 'rb')
        print 'killing...'
        pid = int(file.readline())
        os.kill(pid, signal.SIGINT)
        time.sleep(2)
    except IOError:
        # the pid file has been deleted
        pass
    except OSError, data:
        print data

# args: a list of string arguments
#
def launchFSAdm(args):
    cmd = ['%s/%s' % (getLocalFSBinRoot(), FSADM_PROG_NAME)]
    cmd += args
    printCmd(cmd)
    (stdin, stdouterr) = os.popen4(cmd)
    lines = stdouterr.readlines()
    for line in lines: print FSADM_PROG_NAME + '>', line,
    if lines: raise case.Failure, FSADM_PROG_NAME + ' failed'

def getFSAdmDaemonLogBaseName():
    return '%s.%d' % (FSADM_UNIX_NAME, case.getSysId())

def getControllerFSAdmDaemonLogFilePath():
    return os.path.join(case.getControllerLogDir(),
                        getFSAdmDaemonLogBaseName())

def getFSAdmDaemonLogFilePath():
    return os.path.join(case.getLogDir(), 
                        getFSAdmDaemonLogBaseName())

# args: a list of string arguments
#
def launchFSAdmDaemon(args):
    cmd = ['%s/%s' % (getLocalFSBinRoot(), FSADM_PROG_NAME), 
           '-d', getFSAdmDaemonLogFilePath()] 
    cmd += args
    printCmd(cmd)
    os.spawnv(os.P_WAIT, cmd[0], cmd)

def killFSAdmDaemon():
    os.system("killall " + FSADM_PROG_NAME)
        
# online: True or False
#
def setOnline(online):
    if online: online = 'online'
    else:      online = 'offline'
    launchFSAdm(['cmd', getLocalMountPoint(), online])

# @param content     must be one line only
# @param mutable     true: return until the expected content appears
#                    false: raise a case.Failure if the file content is not
#                           empty and is not identical to what's expected
#
def waitFile(path, content, mutable = False):
    assert content
    while 1:
        time.sleep(1)
        if not os.access(path, os.F_OK): continue
    
        file = open(path, 'rb')
        line = file.readline()
        file.close()
        # the file might be initially empty when created
        if not line: continue
        if line != content:
            if mutable: continue
            else: raise case.Failure, 'string mismatch. expect "%s" ' \
                                'actual "%s" in file %s' % (str, line, path)
        break

def waitDir(path):
    while 1:
        time.sleep(1)
        if not os.access(path, os.F_OK): continue
        if not os.path.isdir(path):
            raise case.Failure, path + ' is not a directory'
        break