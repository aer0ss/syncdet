#!/usr/bin/env python

import sys, optparse, os, os.path

try:
    import deploy.syncdet.config
except ImportError:
    print 'Couldn\'t load config.py. Did you "cp ' + \
            os.path.join(sys.path[0], 'config.py.sample') + ' ' + \
            os.sep + os.path.join('etc', 'syncdet', 'config.py') + \
            '" and modify its content?'
    sys.exit(1)

import controller.scn
import controller.report
import controller.deployer
import controller.sync_service
from deploy.syncdet import actors, param

class FlushingOutputStream:
    """
    A wrapper class to another stream class. It flushes the wrapped stream class
    on every write.
    """

    def __init__(self, stream):
        self._stream = stream

    def write(self, data):
        self._stream.write(data)
        self._stream.flush()

    def flush(self):
        self._stream.flush()

def main():

    # We need to constantly flush stdout or "ant syncdet" would buffer console
    # output instead of giving immediate feedback. see also
    # syncdet_case_launcher.py
    sys.stdout = sys.stderr = FlushingOutputStream(sys.stdout)

    # argument parsing

    usage = "usage: %prog [options] deployment_folders..."
    parser = optparse.OptionParser(usage)

    parser.add_option("-s", "--scenario", dest = "scnfile",
                      help = "specify the scenario file. default.scn is the default",
                      metavar = "FILE")
    parser.add_option("-c", "--case", dest = "case",
                      help = "specify a single case, CASE, to run",
                      metavar = "CASE")

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
                      help = "kill all remaining remote sessions and quit")
    parser.add_option("--purge-log", dest = "purge", action = "store_true",
                      default = False,
                      help = "empty the log directory and then quit")

    options, args = parser.parse_args()

    # purge?
    if options.purge:
        controller.purge_log_files()
        sys.exit()

    # clobber?
    if options.clobber:
        controller.kill_all_remote_instances(options.verbose)
        sys.exit()

    # parse deploy folders
    if len(args) < 1:
        print 'Please specify at least one deployment folder. Use --help for usage.'
        sys.exit()

    # add SyncDET's internal deployment folder to the deployment folder list.
    deployFolders = list(args)
    deployFolders.append(os.path.join(sys.path[0], 'deploy'))
    controller.deployer.set_deploy_folders(deployFolders)

    # initialize the actors
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
        scn = controller.scn.compile_single_case(options.case)
    elif options.scnfile:
        scn = controller.scn.compile(options.scnfile)
    else:
        print "Either a scenario file or a test case must be specified." \
                " Use --help for usage."
        sys.exit()

    # launch the sync service
    controller.sync_service.start_service(options.verbose)

    if not options.verify:
        controller.deployer.deploy()

    # launch the global scenario
    controller.scn.execute(scn, '', options.verify, options.verbose)

    if not options.verify and controller.report.report_path():
        print 'the report is at', controller.report.report_path()

if __name__ == '__main__':
    main()
