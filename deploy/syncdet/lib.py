"""This file contains utility functions that are available to both test cases
and the controller. We name this module in such a way that 3rd-party test cases
can't easily run into the same name.
"""

import os.path
import param

def get_log_folder_path(root, scenarioId):
    """
    Return the log folder path given the SyncDET root path and the scenario id
    """
    return os.path.join(root, param.LOG_DIR, scenarioId);

def get_log_file_path(pathLogFolder, module, instId, actorId, suffix = ''):
    """
    Return the log file path
    """
    if suffix is not '': suffix = '-' + suffix;
    unique = get_instance_unique_string(module, instId)
    name = unique + '-{0}{1}.log'.format(actorId, suffix)
    return os.path.join(pathLogFolder, name)

def get_background_pid_file_path(root, key):
    """
    Return the PID file path for background processes launched by
    background.start_process()
    """
    return os.path.join(root, param.BKGND_PID_DIR, '{0}.pid'.format(key))

def get_instance_unique_string(module, instId):
    """
    Return a string unique for every test case instance
    """
    return '{0}-{1}'.format(module, instId)

