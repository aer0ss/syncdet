import sys, os.path

# unlike other scripts, we're invoked from the current directory. 
# we should include the DET root path to let all imports work.
sys.path.insert(1, os.path.normpath(os.path.join(sys.path[0] , '../')))

from syncdet_case_lib import * #@UnusedWildImport

# add the module's parent directory. argv[6] is the directory name relative
# to SyncDET's path.
#
sys.path.insert(1,
    os.path.normpath(os.path.join(sys.path[0] , '../', sys.argv[6])))

# import the case module
exec 'import ' + getCaseModuleName()

class Output:
    fout = None
    newline = 1
    
    def __init__(self, logPath):
        if config.CASE_LOG_OUTPUT: 
            logPath = os.path.normpath(os.path.expanduser(logPath))
            try:
                self.fout = open(logPath, 'a')
            except IOError:
                s_logDir = os.path.dirname(logPath)
                os.makedirs(s_logDir)
                self.fout = open(logPath, 'a')

    def __del__(self):
        if self.fout:
            self.fout.close()
        
    def write(self, data):
        end = -1
        while 1:
            if config.CASE_SCREEN_OUTPUT and self.newline:
                sys.__stdout__.write(config.CASE_OUTPUT_PREFIX % (getSysId()))
            start = end + 1
            end = data.find('\n', start)
            if end < 0:
                if (start < len(data)):
                    self.writeRaw(data[start:])
                    self.newline = 0
                return
            else:
                self.writeRaw(data[start : end + 1])
                self.newline = 1
                # if the '\n' is the last char
                if end == len(data) - 1: return
            
    def writeRaw(self, data):
        if config.CASE_LOG_OUTPUT:    self.fout.write(data)
        if config.CASE_SCREEN_OUTPUT: sys.__stdout__.write(data)

    def fileno(self):
        return self.fout.fileno()

# hijack the stdout and stderr
sys.stdout = sys.stderr = Output(getLogFilePath())

SPEC_NAME = 'spec'

try:
    # execute the right entry point
    spec = eval(getCaseModuleName() + '.' + SPEC_NAME)
    if 'entries' in spec.keys() and getSysId() < len(spec['entries']):
        ret = spec['entries'][getSysId()]()
    else:
        ret = spec['default']()
    if ret: print 'CASE_OK:', str(ret)
    else:   print 'CASE_OK'

except RuntimeError, data:
    failTestCase(str(data))
    
