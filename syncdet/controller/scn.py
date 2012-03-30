import sys, threading, time, random, os, signal
import controller_lib, config, scncc, scnpp, controller, log

INDENT = 4

s_scenarioId = controller_lib.generateTimeDerivedId(False)

def getScenarioId():
    return s_scenarioId

# resolve a list of items and return a list of basic items
#
# NOTE: we resolve names here but not in compile time is to avoid
#       complaint about forward references.
#
def itemsToBasicItems(scn, items):
    list = []
    for item in items:
        list.extend(resolveReference(scn, item))
    return list

# given one item, return a list of basic items
#
def resolveReference(scn, item, list = None):
    if list == None: list = []

    if isinstance(item, scncc.Unit):
        # it's a unit
        list.append(item)
        return list
    else:
        assert isinstance(item, scncc.Object)
        name = item.name
        pos = name.find('(')
        if pos == -1:
            # it's a module name
            list.append(item)
        elif name[:pos] in scn.children.keys():
            # it refers to a Scenario oject
            list.append(scn.children[name[:pos]])
        elif name[:pos] in scn.groups.keys():
            # it refers to a Group oject
            for member in scn.groups[name[:pos]]:
                resolveReference(scn, member, list)
        elif scn.parent:
            resolveReference(scn.parent, item, list)
        else:
            print "error: no group or scenario named '%s' is found" % item
            sys.exit()

    return list

def ind2space(ind):
    return ' ' * ind

# used in the parallel mode
#
class ThdExecBasicItem(threading.Thread):
    scn = None
    item = None
    verify = None
    show = None
    verbose = None
    ind = None
    index = None

    def __init__(self, scn, item, verify, show, verbose, ind, index):
        threading.Thread.__init__(self)
        self.scn = scn
        self.item = item
        self.verify = verify
        self.show = show
        self.verbose = verbose
        self.ind = ind
        self.index = index

        self.setDaemon(True)

    def run(self):
        executeBasicItem(self.scn, self.item, self.verify, self.show,
                    self.verbose, self.ind, self.index)

def executeBasicItem(scn, bi, verify, show, verbose, ind, index):
    '''@param bi: type: scncc.Unit. Refers to a basic item.'''
    ind = ind + INDENT
    if isinstance(bi, scncc.Scenario):
        # it's a scenario
        executeUnit(bi, bi.unit, verify, show, verbose, ind)
    elif isinstance(bi, scncc.Unit):
        # it's a unit
        executeUnit(scn, bi, verify, show, verbose, ind)
    else:
        assert isinstance(bi, scncc.Object)
        # it's a module
        if show: print ind2space(ind) + bi.name + ' %d' % index
        if verify: return
        ret = controller.executeCase(bi.name, bi.dir, verbose)
        if not ret and scn.nofail:
            print ">>>>>> Force to quit because of 'nofail'. It may generate "\
                    "some exceptions. Please ignore."
            # this will be caught by executeUnit
            os.kill(os.getpid(), signal.SIGINT)
            # in case the signal is lost
            sys.exit()

def executeUnit(scn, unit, verify, show, verbose, ind):
    if unit.action == scncc.SERIAL:
        if show: print ind2space(ind) + 'SERIAL,' + str(unit.count)
        basicItems = itemsToBasicItems(scn, unit.children)
        for bi in basicItems:
            if unit.count == 0:
                i = 0
                while 1:
                    executeBasicItem(scn, bi, verify, show, verbose, ind, i)
                    i += 1
            else:
                for i in xrange(unit.count):
                    executeBasicItem(scn, bi, verify, show, verbose, ind, i)

    elif unit.action == scncc.PARALLEL:
        if show: print ind2space(ind) + 'PARALLEL,' + str(unit.count)
        assert unit.count != 0

        basicItems = itemsToBasicItems(scn, unit.children)
        thds = []
        for bi in basicItems:
            for i in xrange(unit.count):
                thd = ThdExecBasicItem(scn, bi, verify, show, verbose, ind, i)
                thd.start()
                thds.append(thd)
                if config.PARALLEL_DELAY: time.sleep(config.PARALLEL_DELAY)

        # wait for threads to complete. As executeCase() has its own timeout
        # control. we don't manage timeouts here.
        for thd in thds:
            thd.join()
        if show: print ind2space(ind) + 'END PARALLEL,' + str(unit.count)

    else:
        if show: print ind2space(ind) + 'SHUFFLE,' + str(unit.count)
        # we use a separate randomizer per shuffle because of multi-threading
        rand = random.Random()

        basicItems = itemsToBasicItems(scn, unit.children)
        if unit.count == 0: count = len(basicItems)
        else: count = unit.count

        i = 0
        refill = -1
        remains = []
        while i < count:
            # refill
            if not remains:
                remains.extend(basicItems)
                refill += 1
            luck = rand.randint(0, len(remains) - 1)
            executeBasicItem(scn, remains.pop(luck), verify, show, verbose, ind, refill)
            i += 1

# this's a naive way to prevent reference recursion
#
def executeUnitSafe(scn, unit, verify, show, verbose, ind):
    try:
        executeUnit(scn, unit, verify, show, verbose, ind)
    except RuntimeError:
        print 'error: recursive referencing exists in the scenario file.'

# scenario: if no scenario then the global scenario will be executed
#
def execute(glob, scenario, verify, verbose):

    show = True

    if not scenario:
        scn = glob
    elif scenario not in glob.children.keys():
        print "scenario '%s' not found" % scenario
        sys.exit()
    else:
        scn = glob.children[scenario]

    try:
        log.createLogFolders(verify)

        # global opening
        ocUnit = scncc.Unit(scncc.SERIAL, 1)
        if glob.opening:
            if verify or verbose: print 'OPENING'
            ocUnit.children = glob.opening
            oldnf = glob.nofail
            glob.nofail = True
            executeUnitSafe(glob, ocUnit, verify, show, verbose, INDENT)
            glob.nofail = oldnf

        if scn != glob:
            if verify or verbose: print scn.name

        # scenario opening
        if scn != glob and scn.opening:
            if verify or verbose: print ind2space(INDENT) + 'OPENING'
            ocUnit.children = scn.opening
            oldnf = scn.nofail
            scn.nofail = True
            executeUnitSafe(scn, ocUnit, verify, show, verbose, INDENT * 2)
            scn.nofail = oldnf

        # scenario body
        if scn != glob: ind = INDENT
        else: ind = 0
        executeUnitSafe(scn, scn.unit, verify, show, verbose, ind)

        # scneario closing
        if scn != glob and scn.closing:
            if verify or verbose: print ind2space(INDENT) + 'CLOSING'
            ocUnit.children = scn.closing
            executeUnitSafe(scn, ocUnit, verify, show, verbose, INDENT * 2)

        # global closing
        if glob.closing:
            if verify or verbose: print 'CLOSING'
            ocUnit.children = glob.closing
            executeUnitSafe(glob, ocUnit, verify, show, verbose, INDENT)

        # even though we collect case-specific log files after each test case,
        # there might be more log files to collect (e.g. the ones generated by
        # subprocesses)
        log.collectAllLogs()

    except KeyboardInterrupt:
        # this will also finish the rsh processes on the local actor
        controller.killAllRemoteInstances(verbose)

def compileSingleCase(case, dir): return scncc.compileSingleCase(case, dir)

def compile(path):
    tmp = scnpp.preprocess(path)
    # scnpp.printResult(tmp)
    return scncc.compile(tmp, path)
    tmp.close()
