#!/usr/bin/python

import sys, optparse

import controller.scn
import controller.syncsvc
import controller.report
import controller.lib
import controller.deploy
import controller
import systems
import config

# argument parsing

usage = "usage: %prog [options] scenario"
parser = optparse.OptionParser(usage)

parser.add_option("-f", "--scenario", dest="scnfile", default="default.scn",
                  help="specify the scenario file. default.scn is the default",
                  metavar="FILE")
parser.add_option("-c", "--case", dest="case",
                  help="specify a single case, CASE, to run. Change the Python"\
                  " root directory to DIR before running. DIR must be relative"\
                  " to SyncDET's root directory",
                  metavar="DIR,CASE")

parser.add_option("-m", "--systems", dest="systems", type="int", default="-1",
                  help="the max number of systems to use. use all sytems "\
                  "otherwise", metavar="N")
parser.add_option("-t", "--case-timeout", dest="casetimeout", type="int",
                  help="the case timeout, overwriting config.CASE_TIMEOUT",
                  metavar="TIMEOUT")
parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                  default=False,
                  help="verbose mode")
parser.add_option("-e", "--verify", dest="verify", action="store_true",
                  default=False,
                  help="print but not actually run the cases")

parser.add_option("--clobber", dest="clobber", action="store_true",
                  help="kill all remaning remote sessions and quit")
parser.add_option("--purge-log", dest="purge", action="store_true",
                  default=False,
                  help="empty the log directory and then quit")

options, args = parser.parse_args()

# purge?
if options.purge:
    controller.purgeLogFiles()
    sys.exit()

# clobber?
if options.clobber:
    controller.killAllRemoteInstances(options.verbose)
    sys.exit()

# find out the scenario
if not len(args):
    scenarios = ['']
else:
    scenarios = args

# initialize the systems, and 
if options.systems != -1:
    systems.init(options.verbose, options.systems)
else:
    systems.init(options.verbose)

# case timeout?
if options.casetimeout:
    config.CASE_TIMEOUT = options.casetimeout
    
# compile the scenario file
# is a single case specified?
if options.case:
    items = options.case.split(',')
    if len(items) != 2:
        parser.print_help()
        sys.exit()
    scn = controller.scn.compileSingleCase(items[1], items[0])
else:
    scn = controller.scn.compile(options.scnfile)

# launch the sync service
controller.syncsvc.startService(options.verbose)

if config.DIRECTORY_SHARING == True:
    print 'error: there previously existed support for ' \
          'DIRECTORY_SHARING=True (ie a shared NFS drive), ' \
          'but now we assume this not to be the case.'
    sys.exit()
else:
    controller.deploy.deployActorSrc()

# launch the scenarios
for scenario in scenarios:
    controller.scn.execute(scn, scenario, options.verify, options.verbose)

if not options.verify and controller.report.getReportPath():
    print 'the report is at', controller.report.getReportPath()
        
