import os.path, multiprocessing
import sys

from deploy.syncdet import actors, param

global _normalizedPaths # I hate globals
global _localRoots

def set_deploy_folders(folders):
    global _normalizedPaths
    _normalizedPaths = []
    global _localRoots
    _localRoots = []
    for folder in folders:
        path, localRoot = _normalize_path(folder)
        assert os.path.exists(path), "deploy path {} does not exist".format(path)
        _normalizedPaths.append(path)
        _localRoots.append(localRoot)

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

def deploy_folder_local_roots():
    """
    Return the list of local roots of the deploy folders passed into
    method setDeployFolders(). See _normalizePath() for the definition of local
    roots.
    """
    return _localRoots

def deploy():
    """
    Deploy all the deployment folders.
    """
    print "deploying..."

    pool = multiprocessing.Pool()
    pool.map(_rsync, actors.actor_list())

    print "done"

def _rsync(actor):
    """
    @param actor type: actors.Actor
    """
    dst = os.path.join(actor.root, param.DEPLOY_DIR)
    actor.rsync(_normalizedPaths, dst)
