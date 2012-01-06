import os, string, time, datetime, signal, sys, threading, os.path

import config, systems, report, lib, scn

WRAPPER_NAME = 'syncdet_actor_wrapper.py'

SPEC_NAME = 'spec'

def errorAnalysis(msg):
    print 'error:', msg
    sys.exit()
    
# return: the number of systems to launch, and the case timeout value
def analyze(module, dir):
    try:
        sys.path.insert(0, os.path.join(lib.getLocalRoot(), dir))
        exec 'import ' + module
        sys.path.pop(0)
    except ImportError, data:
        errorAnalysis("cannot import module '%s': %s" % (module, data))
    
    if SPEC_NAME not in eval(module + '.__dict__'):
        errorAnalysis("module '%s' has no '%s' defined" % (module, SPEC_NAME))
    
    try:
        spec = eval(module + '.' + SPEC_NAME)
        if 'entries' not in spec.keys() and 'default' not in spec.keys():
            raise Exception
        
        n = lib.getSysCount()
        prefered = 0
        if 'entries' in spec.keys():
            prefered += len(spec['entries'])
            # number of systems must meet the minimum req.
            if (n < prefered):
                 errorAnalysis(module + " requires at least %d systems but " \
                                      "we only have %d." % (prefered, n))

        if 'max_add' in spec.keys():
            prefered += spec['max_add']
        elif 'default' in spec.keys():
            prefered = -1
        
        if 'timeout' in spec.keys():
            timeout = spec['timeout']
        else:
            timeout = config.CASE_TIMEOUT
    except Exception: 
        errorAnalysis(module + " has an invalid '" + SPEC_NAME + "' structure.")

    if prefered == -1:
        return n, timeout
    else:
        if not prefered: 
            print "warning: '%s' specifies zero systems to run, please check "\
            "its '%s' data structure." % (module, SPEC_NAME)
        return min(n, prefered), timeout
    
# return the pid of the local proxy process. cmd is a string
#
def executeRemoteCmd(sysId, cmd, verbose):
    system = systems.systems[sysId]
    args = [
           system['rsh'],
           system['login'] + '@' + system['address'],
           cmd
           ]
    if verbose:
        print 'cmd[%d]' % sysId,
        for arg in args: print arg,
        print 
    return os.spawnvp(os.P_NOWAIT, args[0], args)

# return the number of systems and a list of systems that didn't finish on time
#
def launchCase(module, dir, instId, verbose):
    n, timeout = analyze(module, dir)
        
    pids = {}    # { pid: sysId }
    for i in range(n):
        system = systems.systems[i]
        # the command
        cmd =  'python %s/case/%s ' % (system['detRoot'], WRAPPER_NAME)
        # the arguments:
        # module sysId scenarioId instId sysCount dir(relative to SyncDET root) controllerRoot
        cmd += '%s %d %s %s %d %s %s' % (module, i, 
                                      scn.getScenarioInstanceId(), 
                                      instId, n, dir, lib.getLocalRoot())

        pids[executeRemoteCmd(i, cmd, verbose)] = i

    start = time.time()
    while 1:
        # iterate all pids that we're waiting
        for pid in pids.keys():
            pid2, exit = os.waitpid(pid, os.WNOHANG)
            if not pid2: continue
            assert(pid == pid2)
            if verbose: print 'sys %d finished' % pids[pid]
            del pids[pid]    
        if not pids: break
        if time.time() - start > timeout:
            if verbose: print '%s timed out' % module
            break
        time.sleep(1)
        
    # kill unfinished systems
    for pid in pids.keys():
        if verbose: print 'killing sys %d' % pids[pid]
        # kill the local process first
        os.kill(pid, signal.SIGKILL)
        killRemoteInstance(pids[pid], instId, verbose)
        
    return n, pids.values()

s_lock = threading.Lock()

def makeCaseInstanceId():
    # lock to prevent coincidents on multi-processors
    global s_lock
    s_lock.acquire()
    now = datetime.datetime.today()
    s_lock.release()
    return string.translate(str(now), string.maketrans(' :', '-.'))

# return False if the case failed
#
def executeCase(module, dir, verbose):
    instId = makeCaseInstanceId()
    n, unfinished = launchCase(module, dir, instId, verbose)
    return report.reportCase(module, instId, n, unfinished)

KILL_CMD = "for i in `ps -eo pid,cmd | grep '%s' | grep -v grep | " \
            "sed 's/ *\\([0-9]*\\).*/\\1/'`; do kill $i; done"

def killRemoteInstance(sysId, instId, verbose):
    # instId uniquely identifies the case instance
    cmd =  KILL_CMD % instId
    executeRemoteCmd(sysId, cmd, verbose)
    
    # don't cancel. let sync GC do the work
    # cancel the synchronizer
    # time.sleep(config.SYNC_CANCEL_DELAY)
    # sync.cancelSynchronizers(instId)
        
def killAllRemoteInstances(verbose):
    cmd = KILL_CMD % WRAPPER_NAME
    for i in range(lib.getSysCount()): executeRemoteCmd(i, cmd, verbose)
        
def purgeLogFiles():
    os.system('rm -rf %s/%s/*' % (lib.getLocalRoot(), config.LOG_DIR))
