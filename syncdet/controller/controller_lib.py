import sys, os.path, datetime, time

s_pathRoot = os.path.realpath(os.path.expanduser(sys.path[0]))

def getRootPath(): return s_pathRoot

def generateTimeDerivedId(includeMSec):
    '''Generate a string based on the current time. the string can be used as
    identifier of test executions, etc
    '''
    now = datetime.datetime.today()
    ret = '%d.%02d.%02d.%02d%02d%02d' % (now.year, now.month, now.day,
                                            now.hour, now.minute, now.second)
    if includeMSec:
        ret += '.' + str(int(round(time.time() * 1000)) % 1000)

    return ret
