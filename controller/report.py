import threading, os.path

import scn
from deploy.syncdet import param
import lib, log

RES_OK = 0
RES_NOSTART = 1
RES_FAIL = 2
RES_TERM = 3
RES_TIMEOUT = 4

def is_report_enabled():
    return param.CASE_LOG_OUTPUT and param.CASE_REPORT

# static initialization
#
if is_report_enabled():
    s_reportPath = '{0}/{1}/report-{2}.txt'.format(lib.root_path(),
           param.REPORT_DIR, scn.scenario_id())
    d = os.path.dirname(s_reportPath)
    if not os.path.exists(d): os.mkdir(d)
    s_reportFile = None    # open the file only when generating the report
    s_lock = threading.Lock()

# return '' if reporting is not enabled
def report_path():
    if not is_report_enabled(): return ''
    global s_reportPath
    return s_reportPath

# return False if the case failed
# TODO: synchronization
#
def report_case(module, caseInstId, n, unfinished):
    if not is_report_enabled(): return True

    results = []    # [[RES_*, explanation]]
    for i in range(n):
        if i in unfinished:
            results.append([RES_TIMEOUT, ''])
            continue

        try:
            logpath = log.controller_scenario_log_file(i, module, caseInstId)
            f = open(logpath, 'r')
        except IOError:
            results.append([RES_NOSTART, 'please check e.g. actors.py'])
            continue

        while 1:
            line = f.readline()
            if not line:
                code = RES_TERM
                text = ''
                break
            ind = line.find('CASE_OK')
            if ind != -1:
                code = RES_OK
                if line.find('CASE_OK:') != -1: text = line[len('CASE_OK: '):-1]
                else: text = ''
                break
            ind = line.find('CASE_FAILED: ')
            if ind != -1:
                code = RES_FAIL
                text = line[ind + len('CASE_FAILED: '):-1]
                break
        f.close()

        results.append([code, text])
        continue

    # if the case succeeded and had no outputs?
    okay = True
    text = False
    for i in range(n):
        if results[i][0] != RES_OK:
            okay = False
        if results[i][1]:
            text = True

    global s_lock
    s_lock.acquire()

    global s_reportFile
    if not s_reportFile:
        s_reportFile = open(s_reportPath, 'w')

    logpath = log.controller_scenario_log_file(0, module, caseInstId)

    if okay:
        s_reportFile.write('OK     %s\t%s\n' % (module, logpath))
    else:
        s_reportFile.write('FAILED %s\t%s\n' % (module, logpath))
        print 'FAILED. see report', report_path()

    if not okay or text:
        for i in range(n):
            s_reportFile.write('    actor %d: ' % i)

            if results[i][0] == RES_OK:
                s_reportFile.write('OK.       ')
            elif results[i][0] == RES_NOSTART:
                s_reportFile.write('failed to start.')
            elif results[i][0] == RES_FAIL:
                s_reportFile.write('failed.   ')
            elif results[i][0] == RES_TERM:
                s_reportFile.write('quit abnormally.')
            elif results[i][0] == RES_TIMEOUT:
                s_reportFile.write('timed out.')

            s_reportFile.write(' ' + results[i][1] + '\n')

    # to let the user read the error report ASAP
    s_reportFile.flush()

    # unlock
    s_lock.release()

    return okay
