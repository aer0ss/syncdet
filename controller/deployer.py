import os.path, multiprocessing
import sys

from deploy.syncdet import actors, param

global _normalizedPaths # I hate globals
global _localRoots

def setDeployFolders(folders):
    global _normalizedPaths
    _normalizedPaths = []
    global _localRoots
    _localRoots = []
    for folder in folders:
        path, localRoot = _normalizePath(folder)
        _normalizedPaths.append(path)
        _localRoots.append(localRoot)

def _normalizePath(path):
    """
    Return normalized paths to satisfy rsync's syntax. Specifically, this
    method adds '/./' to the end of the path if this string is not found in the
    path. Also returned is the local root, which equals path[:pos], where pos
    is the position the substring '/./' starts, or the end of path if the
    string is not found. For example:

    Given '/foo/./bar', the method returns ['/foo/./bar', '/foo'].
    Given '/foo/bar', the method returns ['/foo/bar/./', '/foo'].
    """
    slashDotSlash = os.sep + '.' + os.sep

    pos = path.find(slashDotSlash)
    if pos is not -1:
        return path, path[ : pos]
    else:
        return path + slashDotSlash, path

def getDeployFolderLocalRoots():
    """
    Return the list of local roots of the deploy folders passed into
    method setDeployFolders(). See _normalizePath() for the definition of local
    roots.
    """
    return _localRoots

def deploy():
    """
    Deploy all the deployment folders.
    @param deployFolders: type a list of strings. specifies the user-defined
    folders to deploy.
    """
    print "deploying..."
    sys.stdout.flush()

    pool = multiprocessing.Pool()
    pool.map(_rsync, actors.getActors())

    print "done"
    # We need a flush here or output from test cases would mythically appear
    # before "done".
    sys.stdout.flush()

def _rsync(actor):
    """
    @param actor: type: actors.Actor
    """
    dst = os.path.join(actor.root, param.DEPLOY_DIR)
    actor.rsync(_normalizedPaths, dst)
