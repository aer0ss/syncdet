#!/usr/bin/env python

import optparse, os, os.path, sys, traceback
import controller.scn
import controller.report
import controller.deployer
import controller.sync_service
from deploy.syncdet import config, actors, param
from controller import log

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

    parser.add_option("-s", "--scenario", dest="scnfile",
                      help="specify the scenario file. default.scn is the default",
                      metavar="FILE")
    parser.add_option("-c", "--case", dest="case",
                      help="specify a single case, CASE, to run",
                      metavar="CASE")
    parser.add_option("--config", dest="config",
                      help="the YAML configuration file to use. Defaults to "\
                      "/etc/syncdet/config.yaml",
                      default="/etc/syncdet/config.yaml")

    parser.add_option("-m", "--actors", dest="actors", type="int", default="-1",
                      help="the max number of actors to use. use all sytems "\
                      "otherwise", metavar="N")
    parser.add_option("-t", "--case-timeout", dest="casetimeout", type="int",
                      help="the case timeout, overwriting param.CASE_TIMEOUT",
                      metavar="TIMEOUT")
    parser.add_option("--sync-timeout", dest="synctimeout", type="int",
                      help="the synchronization timeout, overwriting param.SYNC_TIMEOUT")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      default=False,
                      help="verbose mode")
    parser.add_option("-e", "--verify", dest="verify", action="store_true",
                      default=False,
                      help="print but not actually run the cases")

    parser.add_option("--clobber", dest="clobber", action="store_true",
                      help="kill all remaining remote sessions and quit")
    parser.add_option("--purge-log", dest="purge", action="store_true",
                      default=False,
                      help="empty the log directory and then quit")
    parser.add_option("--team-city", dest="team_city", action="store_true",
                      help="Enable teamcity output (used to gather statistics)")
    parser.add_option("--tar", dest="tar_dir", action="append", type="string", default=[],
                      help="paths to capture in a tar package")

    options, args = parser.parse_args()

    # load the configuration file
    try:
        config.load(os.path.expanduser(options.config))
    except IOError as e:
        # For prettier errors relating to missing config file
        print e
        sys.exit(1)

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
        sys.exit(1)

    # add SyncDET's internal deployment folder to the deployment folder list.
    deploy_folders = list(args)
    deploy_folders.append(os.path.join(sys.path[0], 'deploy'))

    # initialize the actors
    if options.actors != -1:
        actors.init(options.verbose, options.actors)
    else:
        actors.init(options.verbose)

    # case timeout?
    if options.casetimeout:
        param.CASE_TIMEOUT = options.casetimeout

    # sync timeout?
    if options.synctimeout:
        param.SYNC_TIMEOUT = options.synctimeout

    # compile the scenario file
    # is a single case specified?
    if options.case:
        scn = controller.scn.compile_single_case(options.case)
    elif options.scnfile:
        scn = controller.scn.compile(options.scnfile)
    else:
        print "Either a scenario file or a test case must be specified." \
                " Use --help for usage."
        sys.exit(1)

    # launch the sync service
    controller.sync_service.start_service(options.verbose)

    if not options.verify:
        controller.deployer.deploy(deploy_folders, options.config)

    if options.team_city:
        with open("teamcity-info.xml", "w") as tci:
            tci.write("<build>\n")
            tci.write("<statusInfo>\n")
            tci.write("</statusInfo>\n")
            tci.write("</build>")

    # launch the global scenario
    return_code = 0
    try:
        controller.scn.execute(scn, '', options.verify, options.verbose, options.team_city)
    except Exception as e:
        if options.verbose: traceback.print_exc()
        return_code = 1
    finally:
        if not options.verify and controller.report.report_path():
            print 'the report is at', controller.report.report_path()

        # copy daemon logs and publish (don't use team city if specified because this isn't really a test)
        if len(options.tar_dir) > 0:
            print "tarring ", options.tar_dir
            tar_user_data_scn = controller.scn.compile_single_case("syncdet.case.tar_user_data")
            controller.scn.execute(tar_user_data_scn, '', options.verify, options.verbose, False, *options.tar_dir)

            for id,actor in enumerate(actors.actor_list()):
                log.collect_user_data(id)
                if options.team_city:
                    print "##teamcity[publishArtifacts '" + log.get_user_data_tar_path(id) + "']"

        if options.team_city:
            print "##teamcity[publishArtifacts '" + controller.report.report_path() + "']"

        with open(controller.report.report_path()) as f:
            if "FAILED" in f.read():
                return_code = 1
    return(return_code)

if __name__ == '__main__':
    exit(main())
