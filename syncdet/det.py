#!/usr/bin/python

import sys, optparse

import controller.scn
import controller.report
import controller.deployer
import controller.sync_service
from deploy.syncdet import actors, param

# argument parsing

usage = "usage: %prog [options] scenario"
parser = optparse.OptionParser(usage)

parser.add_option("-f", "--scenario", dest = "scnfile", default = "default.scn",
                  help = "specify the scenario file. default.scn is the default",
                  metavar = "FILE")
parser.add_option("-c", "--case", dest = "case",
                  help = "specify a single case, CASE, to run. Change the Python"\
                  " root directory to DIR before running. DIR must be relative"\
                  " to SyncDET's root directory",
                  metavar = "DIR,CASE")

parser.add_option("-m", "--actors", dest = "actors", type = "int", default = "-1",
                  help = "the max number of actors to use. use all sytems "\
                  "otherwise", metavar = "N")
parser.add_option("-t", "--case-timeout", dest = "casetimeout", type = "int",
                  help = "the case timeout, overwriting param.CASE_TIMEOUT",
                  metavar = "TIMEOUT")
parser.add_option("-v", "--verbose", dest = "verbose", action = "store_true",
                  default = False,
                  help = "verbose mode")
parser.add_option("-e", "--verify", dest = "verify", action = "store_true",
                  default = False,
                  help = "print but not actually run the cases")

parser.add_option("--clobber", dest = "clobber", action = "store_true",
                  help = "kill all remaning remote sessions and quit")
parser.add_option("--purge-log", dest = "purge", action = "store_true",
                  default = False,
                  help = "empty the log directory and then quit")

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

# initialize the actors, and 
if options.actors != -1:
    actors.init(options.verbose, options.actors)
else:
    actors.init(options.verbose)

# case timeout?
if options.casetimeout:
    param.CASE_TIMEOUT = options.casetimeout

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
controller.sync_service.startService(options.verbose)

if not options.verify:
    controller.deployer.deployActorSrc()

# launch the scenarios
for scenario in scenarios:
    controller.scn.execute(scn, scenario, options.verify, options.verbose)

if not options.verify and controller.report.getReportPath():
    print 'the report is at', controller.report.getReportPath()

