import multiprocessing
import sys
import os

from deploy.syncdet import actors, param

global _actor_deploy_roots # I hate globals, but now there is only one

def _normalize_path(path):
    """
    Return normalized paths to satisfy rsync's syntax. Specifically, this
    method adds '/./' to the end of the path if this string is not found in the
    path, and expands the '~' character to the user's home directory. Also
    returned is the local root, which equals path[:pos], where pos
    is the position the substring '/./' starts, or the end of path if the
    string is not found. For example:

    Given '/foo/./bar', the method returns ['/foo/./bar', '/foo'].
    Given '/foo/bar', the method returns ['/foo/bar/./', '/foo'].
    Given '~/foo/bar', the method returns ['/home/user/foo/bar/./', '/home/user/foo']
    """
    path = os.path.expanduser(path)

    slashDotSlash = os.sep + '.' + os.sep

    pos = path.find(slashDotSlash)
    if pos is not -1:
        return path, path[ : pos]
    else:
        return path + slashDotSlash, path

def _normalize_deploy_folders(folders):
    """
    Normalizes each deployment folder specified. Returns
    a list of normalized paths and a list of local roots. See _normalize_path.
    """
    deployment = []
    local_roots = []

    # For each deployment folder specified, normalize the path
    # and append it to the list of folders to deploy
    for folder in folders:
        path, local_root = _normalize_path(folder)
        deployment.append(path)
        local_roots.append(local_root)

    return deployment, local_roots

def _normalize_config_path(config_path):
    """
    The config file must be copied to the actor systems. Since it is one file,
    it will have a different normalization than the deploy folders.
    """
    # Expand ~ to the user's home directory
    config_path = os.path.expanduser(config_path)

    # Normalize the directory in which the config file exists
    normalized_dir, _ = _normalize_path(os.path.dirname(config_path))

    # Append the file name of the config file to the normalized path
    return os.path.join(normalized_dir, os.path.basename(config_path))

def actor_deploy_folder_roots():
    """
    Return the list of local roots of the deploy folders passed into
    method deploy(). See _normalize_path() for the definition of local
    roots.
    """
    return _actor_deploy_roots

def deploy(deploy_folders, config_path):
    """
    Deploy all the deployment folders and the configuration file to actor
    systems.
    """
    # Normalize the deploy folder paths and the config path
    deploy_folders, local_roots = _normalize_deploy_folders(deploy_folders)
    config_path = _normalize_config_path(config_path)

    # Assign the module global variable _actor_deploy_roots, which is used
    # to simulate the actor's PYTHONPATH on the controller system.
    global _actor_deploy_roots
    _actor_deploy_roots = local_roots

    pool = multiprocessing.Pool()

    # Verify that the paths to be deployed exist
    assert all(map(os.path.exists, deploy_folders)), "one of the deploy folders does not exist"
    assert os.path.exists(config_path), "the config file path {} does not exist".format(config_path)

    # Map each actor to an rsync task to run the deployment in parallel.
    # The _rsync_packed() function is used as a proxy so that the multiple arguments
    # needed for _rsync() can be packed into a tuple to satisfy the requirement
    # of 1 argument that pool.map() imposes.
    # *arg magic and lambdas can't be used as they can't be pickled by python
    # (pool.map() crosses process boundaries)
    pool.map(_rsync_packed, [(actor, deploy_folders, config_path) for actor in actors.actor_list()])

    print "done"

def _rsync_packed(packed_args):
    actor, normalized_deploy_folders, normalized_config_path = packed_args
    _rsync(actor, normalized_deploy_folders, normalized_config_path)

def _rsync(actor, normalized_deploy_folders, normalized_config_path):
    """
    @param actor actors.Actor
    @param normalized_deploy_folders list of deployment folders
    @param normalized_config_path a configuration file path
    """
    actor_index = [a.address for a in actors.actor_list()].index(actor.address)
    print 'deploying to {}'.format(actor_index)

    dst = os.path.join(actor.root, param.DEPLOY_DIR)

    # Copy the normalized deploy folders to the destination on the actor
    actor.rsync(normalized_deploy_folders, dst)

    # SyncDET users can specify the path on the controller to the config file,
    # so it must be renamed to a well known name so that actors can find the
    # configuration file. In order to rename the config file, we must make a
    # separate rsync call with a different destination.
    config_dst_path = os.path.join(dst, param.CONFIG_FILE_NAME)
    actor.rsync([normalized_config_path], config_dst_path)

    # Create the user data folder on the actor
    user_data_dir = os.path.join(actor.root, param.USER_DATA_DIR)
    actor.exec_remote_cmd_blocking('mkdir -p {}'.format(user_data_dir))

    print 'deploying to {} done'.format(actor_index)
