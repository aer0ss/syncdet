import sys, threading, time, random
from deploy.syncdet import param
import lib, scncc, scnpp, controller, log

INDENT = 4

s_scenarioId = lib.generate_time_derived_id(False)

def scenario_id():
    return s_scenarioId

# resolve a list of items and return a list of basic items
#
# NOTE: we resolve names here but not in compile time is to avoid
#       complaint about forward references.
#
def items_to_basic_items(scn, items):
    list = []
    for item in items:
        list.extend(resolve_reference(scn, item))
    return list

# given one item, return a list of basic items
#
def resolve_reference(scn, item, list = None):
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
                resolve_reference(scn, member, list)
        elif scn.parent:
            resolve_reference(scn.parent, item, list)
        else:
            print "error: no group or scenario named '%s' is found" % item
            sys.exit(1)

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
    args = None

    def __init__(self, scn, item, verify, show, verbose, team_city_output_enabled, ind, index, args):
        threading.Thread.__init__(self)
        self.scn = scn
        self.item = item
        self.verify = verify
        self.show = show
        self.verbose = verbose
        self.team_city_output_enabled = team_city_output_enabled
        self.ind = ind
        self.index = index
        self.args = args

        self.setDaemon(True)

    def run(self):
        execute_basic_item(self.scn, self.item, self.verify, self.show,
                    self.verbose, self.team_city_output_enabled, self.ind, self.index, *self.args)

def execute_basic_item(scn, bi, verify, show, verbose, team_city_output_enabled, ind, index, *args):
    """
    @param bi: type: scncc.Unit. Refers to a basic item.
    """
    ind = ind + INDENT
    if isinstance(bi, scncc.Scenario):
        # it's a scenario
        execute_unit(bi, bi.unit, verify, show, verbose, team_city_output_enabled, ind, *args)
    elif isinstance(bi, scncc.Unit):
        # it's a unit
        execute_unit(scn, bi, verify, show, verbose, team_city_output_enabled, ind, *args)
    else:
        assert isinstance(bi, scncc.Object)
        # it's a module
        if show: print ind2space(ind) + bi.name + ' %d' % index
        if verify: return
        ret = controller.execute_case(bi.name, verbose, team_city_output_enabled, *args)
        if not ret and scn.nofail:
            print ">>>>>> Force to quit because of 'nofail'. It may generate "\
                    "some exceptions. Please ignore."
            raise Exception("nofail situation encountered")

def execute_unit(scn, unit, verify, show, verbose, team_city_output_enabled, ind, *args):
    if unit.action == scncc.SERIAL:
        if show: print ind2space(ind) + 'SERIAL,' + str(unit.count)
        basicItems = items_to_basic_items(scn, unit.children)
        for bi in basicItems:
            if unit.count == 0:
                i = 0
                while 1:
                    execute_basic_item(scn, bi, verify, show, verbose, team_city_output_enabled, ind, i, *args)
                    i += 1
            else:
                for i in xrange(unit.count):
                    execute_basic_item(scn, bi, verify, show, verbose, team_city_output_enabled, ind, i, *args)

    elif unit.action == scncc.PARALLEL:
        if show: print ind2space(ind) + 'PARALLEL,' + str(unit.count)
        assert unit.count != 0

        basicItems = items_to_basic_items(scn, unit.children)
        thds = []
        for bi in basicItems:
            for i in xrange(unit.count):
                thd = ThdExecBasicItem(scn, bi, verify, show, verbose, team_city_output_enabled, ind, i, args)
                thd.start()
                thds.append(thd)
                if param.PARALLEL_DELAY: time.sleep(param.PARALLEL_DELAY)

        # wait for threads to complete. As executeCase() has its own timeout
        # control. we don't manage timeouts here.
        for thd in thds:
            thd.join()
        if show: print ind2space(ind) + 'END PARALLEL,' + str(unit.count)

    else:
        if show: print ind2space(ind) + 'SHUFFLE,' + str(unit.count)
        # we use a separate randomizer per shuffle because of multi-threading
        rand = random.Random()

        basicItems = items_to_basic_items(scn, unit.children)
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
            execute_basic_item(scn, remains.pop(luck), verify, show, verbose, team_city_output_enabled, ind, refill, *args)
            i += 1

# this's a naive way to prevent reference recursion
#
def execute_unit_safe(scn, unit, verify, show, verbose, team_city_output_enabled, ind, *args):
    try:
        execute_unit(scn, unit, verify, show, verbose, team_city_output_enabled, ind, *args)
    except RuntimeError:
        print 'error: recursive referencing exists in the scenario file.'

# scenario: if no scenario then the global scenario will be executed
#
def execute(glob, scenario, verify, verbose, team_city_output_enabled, *args):

    show = True

    if not scenario:
        scn = glob
    elif scenario not in glob.children.keys():
        print "scenario '%s' not found" % scenario
        sys.exit(1)
    else:
        scn = glob.children[scenario]

    try:
        log.create_log_folders(verify)

        # global opening
        ocUnit = scncc.Unit(scncc.SERIAL, 1)
        if glob.opening:
            if verify or verbose: print 'OPENING'
            ocUnit.children = glob.opening
            oldnf = glob.nofail
            glob.nofail = True
            execute_unit_safe(glob, ocUnit, verify, show, verbose, team_city_output_enabled, INDENT, *args)
            glob.nofail = oldnf

        if scn != glob:
            if verify or verbose: print scn.name

        # scenario opening
        if scn != glob and scn.opening:
            if verify or verbose: print ind2space(INDENT) + 'OPENING'
            ocUnit.children = scn.opening
            oldnf = scn.nofail
            scn.nofail = True
            execute_unit_safe(scn, ocUnit, verify, show, verbose, team_city_output_enabled, INDENT * 2, *args)
            scn.nofail = oldnf

        # scenario body
        if scn != glob: ind = INDENT
        else: ind = 0
        execute_unit_safe(scn, scn.unit, verify, show, verbose, team_city_output_enabled, ind, *args)

        # scneario closing
        if scn != glob and scn.closing:
            if verify or verbose: print ind2space(INDENT) + 'CLOSING'
            ocUnit.children = scn.closing
            execute_unit_safe(scn, ocUnit, verify, show, verbose, team_city_output_enabled, INDENT * 2, *args)

        # global closing
        if glob.closing:
            if verify or verbose: print 'CLOSING'
            ocUnit.children = glob.closing
            execute_unit_safe(glob, ocUnit, verify, show, verbose, team_city_output_enabled, INDENT, *args)

        # even though we collect case-specific log files after each test case,
        # there might be more log files to collect (e.g. the ones generated by
        # subprocesses)
        log.collect_all_logs()

    except KeyboardInterrupt:
        # this will also finish the rsh processes on the local actor
        controller.kill_all_remote_instances(verbose)

def compile_single_case(case): return scncc.compile_single_case(case)

def compile(path):
    tmp = scnpp.preprocess(path)
    # scnpp.printResult(tmp)
    return scncc.compile(tmp, path)
    tmp.close()
