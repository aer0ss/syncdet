import time, signal, sys, threading, os, traceback

from deploy.syncdet import param, actors

import report, scn, log, lib, deployer

_SPEC_NAME = 'spec'

_LAUNCHER_PY = 'syncdet_case_launcher.py'

def errorAnalysis(msg):
    print 'Test code error:', msg
    sys.exit()

def analyze(module):
    """
    @return: the number of actors to launch, and the case timeout value
    """

    # simulate PYTHONPATH on actor systems
    localRoots = deployer.getDeployFolderLocalRoots()
    for f in localRoots: sys.path.insert(0, f)

    try:
        __import__(module)
    except ImportError:
        traceback.print_exc()
        errorAnalysis("cannot import module '{0}'. See above for the backtrace."
                .format(module))
    finally:
        del sys.path[ : len(localRoots)]

    namespace = sys.modules[module].__dict__

    if _SPEC_NAME not in namespace:
        errorAnalysis("module '{0}' has no '{1}' defined"
                .format(module, _SPEC_NAME))

    try:
        spec = namespace[_SPEC_NAME]
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
        errorAnalysis(module + " has an invalid " + _SPEC_NAME + " structure.")

    if preferred == -1:
        return n, timeout
    else:
        if not preferred:
            print "warning: '%s' specifies zero actors to run, please check "\
            "its '%s' data structure." % (module, _SPEC_NAME)
        return min(n, preferred), timeout

def launchCase(module, instId, verbose):
    """
    @return: the number of actors and a list of actors that didn't finish on time
	"""

    n, timeout = analyze(module)

    pids = {}    # { pid: actorId }
    for i in range(n):
        actor = actors.getActor(i)
        # the command
        cmd = 'python {0}/deploy/{1} '.format(actor.root, _LAUNCHER_PY)
        # the arguments:
        # module actorId scenarioId instId actorCount
        cmd += '{0} {1} {2} {3} {4}'.format(
                module, i, scn.getScenarioId(), instId, n)

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
    ret = lib.generateTimeDerivedId(True)
    s_lock.release()
    return ret

def executeCase(module, verbose):
    """
    @return: False if the case failed
    """
    instId = makeCaseInstanceId()
    n, unfinished = launchCase(module, instId, verbose)
    for i in range(n):
        log.collectLog(i, module, instId)
    return report.reportCase(module, instId, n, unfinished)

KILL_CMD = "for i in `ps -eo pid,command | grep '{0}' | grep -v grep | " \
            "sed 's/ *\\([0-9]*\\).*/\\1/'`; do kill $i; done"

def killRemoteInstance(actorId, instId, verbose):
    # instId uniquely identifies the case instance
    cmd = KILL_CMD.format(instId)
    actors.getActor(actorId).execRemoteCmdNonBlocking(cmd)

    # don't cancel. let sync GC do the work
    # cancel the synchronizer
    # time.sleep(param.SYNC_CANCEL_DELAY)
    # sync.cancelSynchronizers(instId)

def killAllRemoteInstances(verbose):
    cmd = KILL_CMD.format(_LAUNCHER_PY)
    for s in actors.getActors(): s.execRemoteCmdNonBlocking(cmd)

def purgeLogFiles():
    os.system('rm -rf {0}/{1}/*'.format(lib.getRootPath(), param.LOG_DIR))
