"""
This module is saved at the same level of the syncdet directory so that
PYTHONPATH is naturally set to the syncdet's parent when this module is
launched. This way, test programs running on actors can refer to syncdet
modules using 'syncdet.foo.'
"""

import sys, traceback

from syncdet import param, case

__import__(case.module_name())

class _MultipleOutputStreams:
    """
    This class duck types the stream interface. It duplicates the input data
    to zero or more stream objects
    """
    streams = None

    def __init__(self, streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)

        # flush on every write. without this:
        #   1. "ant syncdet" would buffer console output instead of giving
        #       immediate feedback. also see syncdet.py
        #   2. on test case timeout, test output would not be recorded in the
        #       log file.
        self.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


class _PrefixOutputStream:
    """
    This class duck types the stream interface. It is a decorator of another
    stream object, adding a prefix string to each line of input data.
    """

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

    def flush(self):
        self.f.flush()

def _redirect_stdout_and_stderr():
    streams = []

    if param.CASE_LOG_OUTPUT:
        path = case.log_file_path()
        streams.append(open(path, 'a'))

    if param.CASE_SCREEN_OUTPUT:
        prefix = param.CASE_OUTPUT_PREFIX.format(case.actor_id())
        stream = _PrefixOutputStream(sys.stdout, prefix)
        streams.append(stream)

    sys.stdout = sys.stderr = _MultipleOutputStreams(streams)

def main():
    _redirect_stdout_and_stderr()

    try:
        # execute the right entry point
        spec = sys.modules[case.module_name()].spec
        if 'entries' in spec.keys() and case.actor_id() < len(spec['entries']):
            ret = spec['entries'][case.actor_id()]()
        else:
            ret = spec['default']()
        if ret: print 'CASE_OK:', str(ret)
        else:   print 'CASE_OK'

    except Exception as data:
        traceback.print_exc()
        case.fail_test_case(str(data))

if __name__ == '__main__':
    main()
