#
# the SyncDET configuration file
#
import getpass

# the address or the host name of the controller
CONTROLLER_ADDR = "192.168.1.30"

# can cases use the console screen as stdout and stderr?
CASE_SCREEN_OUTPUT = True

# log case outputs?
CASE_LOG_OUTPUT = True

# will case results be analyzed and reported?
# ignored if CASE_LOG = False
CASE_REPORT = True

# the default timeout for controller waiting for cases to finish. in sec.
# overwritten by command line option '-t' or spec['timeout']
CASE_TIMEOUT = 60

# the default timeout for synchronizers. in sec.
# overwritten by sync()'s timeout parameter
SYNC_TIMEOUT = CASE_TIMEOUT

# the listening port for the sync service
SYNC_SERVICE_PORT = 2985

# the backlog length for the sync service
SYNC_SERVICE_BACKLOG = 1000

# the prefix for case output. {0} will be replaced by the system id
CASE_OUTPUT_PREFIX = '{0}| '

# the log file directory on each system, relative to DET's root directory
LOG_DIR = 'logs'

# the report directory, relative to DET's root directory
REPORT_DIR = 'reports'

# if the SyncDET directory is shared to the remote systems or not
DIRECTORY_SHARING = False

# the local command to make the file or directory %s remotely writable, if the
# directory is shared to remote systems.
MAKE_SHARED_DIRECTORY_WRITABLE = 'chown ' + getpass.getuser() + ' %s'

# the delay in sec between launches of consecutive parallel items
# this is used to to limit system loads on actors
PARALLEL_DELAY = 0

# the delay before cancelling synchronizers to avoid resurrection due to
# uncleared remote instances
SYNC_CANCEL_DELAY = 3
