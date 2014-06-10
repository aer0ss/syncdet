#
# This file defines SyncDET parameters
#

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

# the default hard timeout for controller waiting for a case to finish. in sec.
# until this point, a case can continue to make progress and a message will be printed
# stating there was a soft timeout
CASE_HARD_TIMEOUT = 180

# the default timeout for synchronizers. in sec.
# overwritten by sync()'s timeout parameter
SYNC_TIMEOUT = CASE_HARD_TIMEOUT

# the listening port for the sync service
SYNC_SERVICE_PORT = 2985

# the listening address for the sync service
SYNC_SERVICE_ADDRESS = "localhost"

# the backlog length for the sync service
SYNC_SERVICE_BACKLOG = 1000

# the prefix for case output
# {0} -> actor id
# {1} -> timestamp on actor
CASE_OUTPUT_PREFIX = '{0}|{1}| '

# The name of the config file on the actor systems. This is a standard name that
# all actors will look for.
CONFIG_FILE_NAME = 'config.yaml'

# the log file directory on each actor, relative to DET's root directory
LOG_DIR = 'logs'

# the report directory, relative to DET's root directory
REPORT_DIR = 'reports'

# the directory containing the background PID files, relative to DET's root
# directory. These files record the PID of the processes launched from
# background.start_process()
BKGND_PID_DIR = 'background'

# the folder name under which deployment folders are copied to actors.
# see case.getDeploymentFolderPath() for details.
DEPLOY_DIR = 'deploy'

# the folder name under which user data are stored on actors.
# see case.getUserDataFolderPath() for details.
USER_DATA_DIR = 'user_data'

# the delay in sec between launches of consecutive parallel items
# this is used to to limit actor loads on actors
PARALLEL_DELAY = 0

# the delay before cancelling synchronizers to avoid resurrection due to
# uncleared remote instances
SYNC_CANCEL_DELAY = 3
