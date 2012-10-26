import sys, os
import scn, lib
import tarfile
from deploy.syncdet import actors, param

import deploy.syncdet.lib
common_lib = deploy.syncdet.lib

_LATEST_LOG_FOLDER_SYMLINK = 'latest'

def create_log_folders(verify):
    """
    Create log folders on both the controller and actors. Although log
    folders on actors can be created lazily when needed, creating it here for
    all actors simplifies collectAllLogs() (as not all actors will be used for
    a scenario) and test cases.
    """
    if verify: return

    # create the log folder regardless of whether logging is enabled, to ensure
    # scenario instances are unique
    scenario_log_path = controller_scenario_log_folder()
    try:
        os.makedirs(scenario_log_path)
    except OSError:
        if not os.path.exists(scenario_log_path):
            print 'Directory ' + scenario_log_path + ' could not be created';
            sys.exit();

    # Create a symlink to the new log folder created above. This is for
    # convenience. The symlink will live in the controller logs folder with
    # the name 'latest'
    try:
        link = os.path.join(common_lib.log_root(lib.root_path()),
                _LATEST_LOG_FOLDER_SYMLINK)

        if os.path.exists(link):
            os.unlink(link)

        os.symlink(scn.scenario_id(), link)
    except OSError:
        # Just output the error, but don't fail
        print "Couldn't create log folder symlink"

    # create log directories on actor actors
    for actor in actors.actor_list():
        path = actor_scenario_log_folder(actor)
        actor.exec_remote_cmd_blocking('mkdir -p ' + path)


def controller_scenario_log_folder():
    """
    @return: the directory where the controller actor stores log files locally
    """
    return common_lib.scenario_log_folder(lib.root_path(),
            scn.scenario_id())

def controller_scenario_log_file(actor_id, module, instance_id):
    """
    @return: the test case log path for the controller actor
    """
    return common_lib.scenario_log_file(controller_scenario_log_folder(), module,
            instance_id, actor_id)

def actor_scenario_log_folder(actor):
    """
    @return: the directory where the actor actor stores log files
    """
    return common_lib.scenario_log_folder(actor.root, scn.scenario_id());

def actor_scenario_log_file(actor, actor_id, module, instance_id):
    """
    @return: the test case log path for the controller actor"""
    return common_lib.scenario_log_file(actor_scenario_log_folder(actor), module,
            instance_id, actor_id)

def collect_log(actor_id, module, instance_id):
    """
    Retrieve the log file of a specific test case instance from a given actor
    actor to the local log directory
    """

    scenario_log_path = controller_scenario_log_file(actor_id, module, instance_id)
    actor = actors.actor(actor_id)
    actor_scenario_log_path = actor_scenario_log_file(actor, actor_id, module, instance_id)
    actor.copy_from(actor_scenario_log_path, scenario_log_path)

def collect_all_logs():
    """
    Retrieve all the log files under the log folders from all the actors to
    the local log directory
    """

    for actor in actors.actor_list():
        scenario_log_path = controller_scenario_log_folder()
        actor_scenario_log_path = actor_scenario_log_folder(actor)
        actor_scenario_log_path = os.path.join(actor_scenario_log_path, "*")

        actor.copy_from(actor_scenario_log_path, scenario_log_path)

def collect_user_data(actor_id):
    """
    Tar the user_data dir into an archive and place in the local log directory
    """
    actor = actors.actor_list()[actor_id]
    scenario_log_path = controller_scenario_log_folder()
    actor.copy_from('user_data-{}.tar'.format(actor_id), scenario_log_path)

def get_user_data_tar_path(actor_id):
    scenario_log_path = controller_scenario_log_folder()
    return os.path.join(scenario_log_path, 'user_data-{}.tar'.format(actor_id))
