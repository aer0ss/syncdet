"""
This file contains utility functions that are available to both test cases
and the controller. We name this module in such a way that 3rd-party test cases
can't easily run into the same name.
"""

import os.path
import param

def log_root(root):
    """
    Return the top level log folder path given the SynDET root
    """
    return os.path.join(root, param.LOG_DIR)

def scenario_log_folder(root, scenario_id):
    """
    Return the log folder path for the given SyncDET root path and scenario id
    """
    return os.path.join(log_root(root), scenario_id);

def scenario_log_file(scn_log_folder_path, module, inst_id, actor_id, suffix = ''):
    """
    Return the log file path
    """
    if suffix is not '': suffix = '-' + suffix;
    unique = instance_unique_string(module, inst_id)
    name = unique + '-{0}{1}.log'.format(actor_id, suffix)
    return os.path.join(scn_log_folder_path, name)

def background_pid_file(root, key):
    """
    Return the PID file path for background processes launched by
    background.start_process()
    """
    return os.path.join(root, param.BKGND_PID_DIR, '{0}.pid'.format(key))

def instance_unique_string(module, inst_id):
    """
    Return a string unique for every test case instance
    """
    return '{0}-{1}'.format(module, inst_id)

