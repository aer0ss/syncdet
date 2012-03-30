import time, signal, sys, threading, os.path

import param, actors, report, scn, deploy, log

from controller_lib import getRootFolderPath, generateTimeDerivedId

WRAPPER_NAME = 'syncdet_actor_wrapper.py'

SPEC_NAME = 'spec'

def errorAnalysis(msg):
    print 'error:', msg
    sys.exit()

def analyze(module, dir):
    '''@return: the number of actors to launch, and the case timeout value
    '''
    try:
        sys.path.insert(0, os.path.join(getRootFolderPath(), dir))
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

        n = actors.getActorCount()
        preferred = 0
        if 'entries' in spec.keys():
            preferred += len(spec['entries'])
            # number of actors must meet the minimum req.
            if (n < preferred):
                errorAnalysis(module + " requires at least %d actors but " \
                               "we only have %d." % (preferred, n))

        if 'max_add' in spec.keys():
            preferred += spec['max_add']
        elif 'default' in spec.keys():
            preferred = -1

        if 'timeout' in spec.keys():
            timeout = spec['timeout']
        else:
            timeout = param.CASE_TIMEOUT
    except Exception:
        errorAnalysis(module + " has an invalid '" + SPEC_NAME + "' structure.")

    if preferred == -1:
        return n, timeout
    else:
        if not preferred:
            print "warning: '%s' specifies zero actors to run, please check "\
            "its '%s' data structure." % (module, SPEC_NAME)
        return min(n, preferred), timeout

def launchCase(module, dir, instId, verbose):
    '''@return: the number of actors and a list of actors that didn't finish 
    on time'''

    n, timeout = analyze(module, dir)

    # Deploy the necessary test case source code to the remote actors
    deploy.deployCaseSrc(dir, [actors.getActor(i) for i in range(n)])

    pids = {}    # { pid: actorId }
    for i in range(n):
        actor = actors.getActor(i)
        # the command
        cmd = 'python {0}/case/{1} '.format(actor.root, WRAPPER_NAME)
        # the arguments:
        # module actorId scenarioId instId actorCount dir(relative to SyncDET root) controllerRoot
        cmd += '{0} {1} {2} {3} {4} {5} {6}'.format(module, i,
                                      scn.getScenarioId(),
                                      instId, n, dir, getRootFolderPath())

        # execute the remote command
        pids[actor.execRemoteCmdNonBlocking(cmd)] = i

    start = time.time()
    while 1:
        # iterate all pids that we're waiting
        for pid in pids.keys():
            pid2, _ = os.waitpid(pid, os.WNOHANG)
            if not pid2: continue
            assert(pid == pid2)
            if verbose: print 'sys %d finished' % pids[pid]
            del pids[pid]
        if not pids: break
        if time.time() - start > timeout:
            if verbose: print '%s timed out' % module
            break
        time.sleep(1)

    # kill unfinished actors
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
    ret = generateTimeDerivedId(True)
    s_lock.release()
    return ret

def executeCase(module, dir, verbose):
    '''@return: False if the case failed'''
    instId = makeCaseInstanceId()
    n, unfinished = launchCase(module, dir, instId, verbose)
    for i in range(n):
        log.collectLog(i, module, instId)
    return report.reportCase(module, instId, n, unfinished)

KILL_CMD = "for i in `ps -eo pid,command | grep '%s' | grep -v grep | " \
            "sed 's/ *\\([0-9]*\\).*/\\1/'`; do kill $i; done"

def killRemoteInstance(actorId, instId, verbose):
    # instId uniquely identifies the case instance
    cmd = KILL_CMD % instId
    actors.getActor(actorId).execRemoteCmdNonBlocking(cmd)

    # don't cancel. let sync GC do the work
    # cancel the synchronizer
    # time.sleep(param.SYNC_CANCEL_DELAY)
    # sync.cancelSynchronizers(instId)

def killAllRemoteInstances(verbose):
    cmd = KILL_CMD % WRAPPER_NAME
    for s in actors.actors: s.execRemoteCmdNonBlocking(cmd)

def purgeLogFiles():
    os.actor('rm -rf %s/%s/*' % (getRootFolderPath(), param.LOG_DIR))
