#
# the scenario file preprocessor
#

import tempfile, sys

TAB_SPACE = 8

def preprocess_file(path, tmp, indent, included):
    try:
        file = open(path, 'r')
    except Exception, data:
        print data
        sys.exit()

    lno = 0
    while 1:
        line = file.readline()
        if not line: break
        lno += 1

        # expand tabs into spaces
        line = line.expandtabs(TAB_SPACE)

        # remove comments
        list = line.split('#', 1)
        if not len(list[0]): continue
        if list[0].isspace(): continue
        line = list[0]

        # calc current indent
        i = 0
        while line[i] == ' ': i += 1
        newindent = indent + i

        words = line.split()
        # preprocess directives
        if words[0] == ':include':
            if len(words) != 2:
                raise Exception, "%s:%d syntax error" % (file.name, lno)
            idx = file.name.rfind('/')
            if idx < 0: include = words[1]
            else: include = file.name[:idx + 1] + words[1]
            if not include in included:
                included.append(include)
                preprocess_file(include, tmp, newindent, included)
        else:
            # output indent
            tmp.write(' ' * newindent)
            # output the content
            for word in words: tmp.write(word + ' ')
            # output path, line number, and \n
            # we use '|' because it can't appear in paths, numbers, or stmts
            tmp.write('|%s|%d\n' % (path, lno))

    file.close()

# return a file handle containing the content ready for the next stage
# the caller should close() the returned value after use
#
# format:
#            stmt |path|line_no
#
#      where path is either an absolute path or a path relative to the current
#      working directory
#
def preprocess(path):
    tmp = tempfile.TemporaryFile()
    preprocess_file(path, tmp, 0, [path])
    tmp.seek(0)
    return tmp

def printResult(tmp):
    print '============ intermidiate file ============='
    for line in tmp.readlines(): print line,
    print '========= END intermidiate file ============'
    tmp.seek(0)
