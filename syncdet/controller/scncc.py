#
# the scenario file compiler
#

import sys, os.path

import lib

# actions for each unit
SERIAL = 0
PARALLEL = 1
SHUFFLE = 2

class Object:
    name = None     # the name of the object
    dir = None      # the directory where the object lives in (only useful
                    # to module names). It's a relative path relative to
                    # the SyncDET root directory

    def __init__(self, name, dir):
        self.name = name
        self.dir = dir

class Unit:
    children = []    # contains Unit objects or Object objects
    action = None
    count = None

    def __init__(self, action, count):
        self.action = action
        self.count = count
        self.children = []

    def __repr__(self):
        if self.action == SERIAL: act = 'SERIAL'
        elif self.action == REPEAT: act = 'REPEAT'
        elif self.action == PARALLEL: act = 'PARALLEL'
        else: act = 'RANDOM'
        return '%s,%d(%s)' % (act, self.count, str(self.children))

class Scenario:
    # contains Scenario's
    children = {}
    # contains Object's
    groups = {}
    # contains Object's
    opening = []
    # contains Object's
    closing = []
    unit = None
    name = None
    parent = None
    nofail = False

    def __init__(self, name, parent, nofail):
        self.children = {}
        self.unit = Unit(SERIAL, 1)    # the pseudo unit
        self.groups = {}
        self.opening = []
        self.closing = []
        self.name = name
        self.parent = parent
        self.nofail = nofail

    def __repr__(self):
        str = "SCENARIO '%s'\n" % self.name
        # if self.parent: str += "  PARENT  '%s'\n" % self.parent.name
        str += '  OPENING %s\n' % self.opening
        str += '  CLOSING %s\n' % self.closing
        str += '  GROUPS  %s\n' % self.groups
        str += '  UNITS   %s\n' % self.unit.children
        # for key in self.children.keys(): str += `self.children[key]`
        return str

class CompileError(Exception):
    pass

def error(path, lno, msg = 'syntax error'):
    raise CompileError, "%s:%d %s" % (path, lno, msg)

# return True if the current block continues. False if it ends
#
def analyzeIndent(file, path, lno, line, stack, canIndent):
    ind = 0
    while line[ind] == ' ': ind += 1

    if (canIndent):
        if len(stack):
            # stop processing if we can indent but we dont. we need to quit
            # one level of recursion but keep the indent stack untouched.
            if ind <= stack[-1]:
                return False
            else:
                stack.append(ind)
                return True
        else:
            stack.append(ind)
            return True
    else:
        if ind == stack[-1]:
            return True
        elif ind <= stack[-2]:
            stack.pop()
            return False
        else:
            error(path, lno, 'confusing indent')

def validSymbol(path, lno, word):
    # check ':'
    if word.find(':') != -1:
        error(path, lno, "cannot use ':' for non-directives")
    # check '(' and ')'
    pos1 = word.find('(')
    pos2 = word.find(')')
    if pos1 != -1 or pos2 != -1:
        if pos1 != len(word) - 2 or pos2 != len(word) - 1:
            error(path, lno, 'error in using parentheses')

# return an Object instance identifying a module, a group, or a scenario
#
def parseObject(path, lno, string):
    words = string.split()
    if len(words) != 1: error(path, lno, 'syntax error')
    validSymbol(path, lno, words[0])

    # get the parent dir of path
    dir = os.path.join(os.getcwd(), os.path.dirname(path))

    # see if the dir is a sub-dir of the local root. Because of aliases,
    # we can't determine it in a simpler way.
    found = False
    tail = len(dir)
    while 1:
        pos = dir[:tail].rfind('/')
        if pos <= 0: break
        if os.path.samefile(dir[:pos], lib.getLocalRoot()):
            found = True
            break
        tail = pos

    # prevent from referencing 'external' modules
    #
    if not found:
        error(path, lno, "it's not safe to execute a module outside the "\
              "SyncDET directory as SyncDET may not properly propagate the "\
              "module to remote systems. It's suggested to create symbolic "\
              "links in the SyncDET directory and use them from there.")
    else:
        # remove the local root prefix. +1 is to remove the '/'
        return Object(string, dir[pos + 1:])

def group1(path, lno, args):
    if (len(args['words'])) != 2: error(path, lno)
    group = args['words'][1]
    validSymbol(path, lno, group)
    scn = args['scn']
    if group in scn.groups.keys():
        error(path, lno, "group '%s' already defined" % group)
    if group in scn.children.keys():
        error(path, lno, "scenario '%s' already defined" % group)

    scn.groups[group] = args['group'] = []

def group2(file, path, lno, stack, line, args):
    args['group'].append(parseObject(path, lno, line))

def unit1(path, lno, args):
    words = args['words']

    # parse the directive
    keys = words[0].split(',')
    if   keys[0] == ':serial':
        action = SERIAL
        count = 1
    elif keys[0] == ':repeat':
        action = SERIAL
        count = 1
    elif keys[0] == ':parallel':
        action = PARALLEL
        count = 1
    elif keys[0] == ':shuffle':
        action = SHUFFLE
        count = 0
    else: error(path, lno)

    # parse the arguments
    if len(keys) > 2: error(path, lno)
    if len(keys) == 2:
        if not keys[1].isdigit(): error(path, lno)
        count = int(keys[1])
        if action == PARALLEL and count == 0:
            error(path, lno, 'the parallel directive can\'t be with 0')

    unit = Unit(action, count)
    args['parent'].children.append(unit)
    args['unit'] = unit

    # add the single object if any
    if len(words) > 2: error(path, lno)
    if len(words) == 2:
        unit.children.append(parseObject(path, lno, words[1]))
        args['singular'] = True

def unit2(file, path, lno, stack, line, args):
    if 'singular' in args.keys():
        error(path, lno, 'singular form of the previous directive '
                            'disallows multiple cases')
    unit = args['unit']
    if line[0] == ':':
        parser(file, path, lno, stack, unit1, unit2,
               words = line.split(), parent = unit)
    else:
        unit.children.append(parseObject(path, lno, line))

def openClose1(path, lno, args):
    words = args['words']
    if (len(words)) > 2: error(path, lno)

    scn = args['scn']
    if (args['act'] == 'open'):
        if scn.opening: error(path, lno, 'opening already defined')
        scn.opening = args['openclose'] = []
    else:
        if scn.closing: error(path, lno, 'closing already defined')
        scn.closing = args['openclose'] = []

    if (len(words)) == 2:
        args['openclose'].append(parseObject(path, lno, words[1]))
        args['singular'] = True


def openClose2(file, path, lno, stack, line, args):
    if 'singular' in args.keys():
        error(path, lno, 'singular form of the previous directive '
                            'disallows multiple cases')
    args['openclose'].append(parseObject(path, lno, line))

def scn1(path, lno, args):
    words = args['words']
    if (len(words)) != 2: error(path, lno)
    validSymbol(path, lno, words[1])
    parent = args['parent']
    if words[1] in parent.children.keys():
        error(path, lno, "scenario '%s' already defined" % words[1])
    if words[1] in parent.groups.keys():
        error(path, lno, "group '%s' already defined" % words[1])

    # check nofail
    nofail = False
    keys = words[0].split(',')
    if len(keys) == 2:
        if keys[1] == 'nofail': nofail = True
        else: error(path, lno)
    elif len(keys) != 1:
        error(path, lno)

    scn = Scenario(words[1], parent, nofail)
    parent.children[words[1]] = scn
    args['scn'] = scn

def scn2(file, path, lno, stack, line, args):
    scn = args['scn']
    words = line.split()
    if words[0] == ':opening':
        parser(file, path, lno, stack, openClose1, openClose2,
               scn = scn, words = words, act = 'open')
    elif words[0] == ':closing':
        parser(file, path, lno, stack, openClose1, openClose2,
               scn = scn, words = words, act = 'close')
    elif words[0] == ':group':
        if 'isglobal' in args:
            parser(file, path, lno, stack, group1, group2,
                   scn = scn, words = words)
        else:
            error(path, lno, "can't define groups in a scenario")
    elif words[0][:4] == ':scn':
        if 'isglobal' in args:
            parser(file, path, lno, stack, scn1, scn2,
                   words = words, parent = scn)
        else:
            error(path, lno, "can't define scenarios in a scenario")
    elif words[0][0] == ':':
        parser(file, path, lno, stack, unit1, unit2,
               words = words, parent = scn.unit)
    else:
        error(path, lno, 'expecting a directive')

def parser(file, path, lno, stack, cbPreamble, cbIteration, **args):
    if cbPreamble: cbPreamble(path, lno, args)

    start = True
    while 1:
        line = file.readline()
        if not line: break
        parts = line.split('|')
        path, lno = parts[-2], int(parts[-1])
        if len(parts) != 3: error(path, lno, "can't have '|'")

        if not analyzeIndent(file, path, lno, parts[0], stack, start):
            # -1 is the '.' after the line number
            file.seek(-len(line), 1)
            break

        # indenting is allowed only at the 1st line of the block
        start = False

        if cbIteration: cbIteration(file, path, lno, stack,
                                    parts[0].strip(), args)

# return the global scenario
#
def compile(file, path):
    try:
        pseudo = Scenario('pseudo', None, False)
        parser(file, path, 0, [], scn1, scn2,
               words = [':scn', 'global'], isglobal = True, parent = pseudo)
    except CompileError, data:
        print data
        sys.exit()

    glob = pseudo.children['global']
    glob.parent = None
    return glob

# compile a single case. dir is the parent directory of the case
#
def compileSingleCase(case, dir):
    glob = Scenario('global', None, False)
    unit = Unit(SERIAL, 1)
    obj = Object(case, dir)

    unit.children.append(obj)
    glob.unit = unit
    return glob
