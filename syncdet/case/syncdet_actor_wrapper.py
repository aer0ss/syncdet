import sys, os.path

# unlike other scripts, we're invoked from the current directory. 
# we should include the DET root path to let all imports work.
sys.path.insert(1, os.path.normpath(os.path.join(sys.path[0] , '../')))

import param
from syncdet_case_lib import getActorId, getLogFilePath, getCaseModuleName, \
        failTestCase

# add the module's parent directory. argv[6] is the directory name relative
# to SyncDET's path.
#
sys.path.insert(1,
    os.path.normpath(os.path.join(sys.path[0] , '../', sys.argv[6])))

# import the case module
exec 'import ' + getCaseModuleName()

class MultipleOutputStreams:
    '''This class duck types the stream interface. It duplicates the input data
    to zero or more stream objects 
    '''
    streams = None

    def __init__(self, streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)

class PrefixOutputStream:
    '''This class duck types the stream interface. It is a decorator of another
    stream object, adding a prefix string to each line of input data.
    '''

    f = None
    prefix = None
    newline = 1

    def __init__(self, f, prefix):
        self.prefix = prefix
        self.f = f;

    def write(self, data):
        end = -1
        while 1:
            if self.newline:
                self.f.write(self.prefix)
            start = end + 1
            end = data.find('\n', start)
            if end < 0:
                if (start < len(data)):
                    self.f.write(data[start:])
                    self.newline = 0
                return
            else:
                self.f.write(data[start : end + 1])
                self.newline = 1
                # if the '\n' is the last char
                if end == len(data) - 1: return

def redirectStdOutAndErr():
    streams = []

    if param.CASE_LOG_OUTPUT:
        path = getLogFilePath()
        streams.append(open(path, 'a'))

    if param.CASE_SCREEN_OUTPUT:
        prefix = param.CASE_OUTPUT_PREFIX.format(getActorId())
        stream = PrefixOutputStream(sys.stdout, prefix)
        streams.append(stream)

    sys.stdout = sys.stderr = MultipleOutputStreams(streams)

def main():
    redirectStdOutAndErr()

    try:
        # execute the right entry point
        spec = eval(getCaseModuleName() + '.spec')
        if 'entries' in spec.keys() and getActorId() < len(spec['entries']):
            ret = spec['entries'][getActorId()]()
        else:
            ret = spec['default']()
        if ret: print 'CASE_OK:', str(ret)
        else:   print 'CASE_OK'

    except RuntimeError, data:
        failTestCase(str(data))

if __name__ == '__main__':
    main()
