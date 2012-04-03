'''This module is saved at the same level of the syncdet directory so that
PYTHONPATH is naturally set to the syncdet's parent when this module is
launched. This way, test programs running on actors can refer to syncdet
modules using 'syncdet.foo.'
'''

import sys

from syncdet import param, case

__import__(case.getModuleName())

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
        path = case.getLogFilePath()
        streams.append(open(path, 'a'))

    if param.CASE_SCREEN_OUTPUT:
        prefix = param.CASE_OUTPUT_PREFIX.format(case.getActorId())
        stream = PrefixOutputStream(sys.stdout, prefix)
        streams.append(stream)

    sys.stdout = sys.stderr = MultipleOutputStreams(streams)

def main():
    redirectStdOutAndErr()

    try:
        # execute the right entry point
        spec = sys.modules[case.getModuleName()].spec
        if 'entries' in spec.keys() and case.getActorId() < len(spec['entries']):
            ret = spec['entries'][case.getActorId()]()
        else:
            ret = spec['default']()
        if ret: print 'CASE_OK:', str(ret)
        else:   print 'CASE_OK'

    except RuntimeError, data:
        case.failTestCase(str(data))

if __name__ == '__main__':
    main()
