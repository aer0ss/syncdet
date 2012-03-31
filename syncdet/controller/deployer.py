#############################################################################
# Deployment Functions:
# - to deploy test case source code to actors
# - to deploy test case source and scenarios to actors
#############################################################################
from multiprocessing import Pool
import os.path, tarfile, lib

from deploy.syncdet import actors

# Tuple of src files which must be deployed for actors to run cases
# - file path relative to syncdet root
# FIXME Putting file names in the source code are fragile. Use the concept of
# workspace as proposed by Allen
ACTOR_PY_FILES = (
                   'deploy/__init__.py',
                   'deploy/syncdet_case_launcher.py',
                   'deploy/syncdet/__init__.py',
                   'deploy/syncdet/actors.py',
                   'deploy/syncdet/param.py',
                   'deploy/syncdet/config.py',
                   'deploy/syncdet/lib.py',
                   'deploy/syncdet/case/__init__.py',
                   'deploy/syncdet/case/case.py',
                   'deploy/syncdet/case/sync.py',
                   'deploy/syncdet/case/background.py',
                  )
ACTOR_TAR_PATH = 'actorsrc.tar.gz'

pool = None

# Deploys the "case/actor" package source code files
# to all known Actors
# - assumes all files in ACTOR_PY_FILES exist locally
def deployActorSrc():
    s_locRoot = lib.getRootPath()

    # Create a tarball of Actor source files
    s_tarPath = createTarFile_(s_locRoot, ACTOR_TAR_PATH, ACTOR_PY_FILES)

    global pool
    if not pool: pool = Pool(actors.getActorCount())
    # For each actor, scp the tar file and extract it
    pool.map(deployTarFileWrapper,
           [TarFileDeployer(s_tarPath, '', actor) for actor in actors.actors])

    # Done with the tar file; locally remove it
    if os.path.exists(s_tarPath): os.remove(s_tarPath)


# Deploys the test case directory of source files to the specified actors
# - relTestDir is relative to SyncDET root directory
CASE_TAR_PATH = 'casesrc.tar.gz'
def deployCaseSrc(s_relTestDir, ls_actors):
    assert len(ls_actors) > 0
    # The following dirname only returns the parent directory if there is
    # no slash at the end of the path.
    if s_relTestDir[-1] == '/': s_relTestDir = s_relTestDir[:-1]
    s_tarPath = createTarFile_(os.path.join(lib.getRootPath(),
                                os.path.dirname(s_relTestDir)),
                                CASE_TAR_PATH,
                                [os.path.basename(s_relTestDir)])

    # For each actor, scp the tar file and extract it
    global pool
    if not pool: pool = Pool(actors.getActorCount())
    pool.map(deployTarFileWrapper,
           [TarFileDeployer(s_tarPath, os.path.dirname(s_relTestDir), actor)
            for actor in ls_actors])

    # Done with the tar file; locally remove it
    if os.path.exists(s_tarPath): os.remove(s_tarPath)

############################################################
# Local helper functions and classes
############################################################

#class SourceCodeDeployer:
#    _actors = []

class TarFileDeployer:
    _s_locTar = ''
    # Directory to extract the tarball, relative to SyncDET root
    _s_dirExtract = ''
    _actor = None
    def __init__(self, s_locTar, s_dirExtract, actor):
        self._s_locTar = s_locTar
        self._s_dirExtract = s_dirExtract
        self._actor = actor
        assert os.path.exists(self._s_locTar)
        assert isinstance(self._actor, actors.Actor)

    def deploy(self):
        # Copy over the tar file to the home directory
        s_dstTar = os.path.join('~', os.path.basename(self._s_locTar))
        self._actor.copyTo(self._s_locTar, s_dstTar)

        # Ensure the destination extraction directory exists
        # Then extract the tar file to that directory and remove the tar
        s_dstdirExtract = os.path.join(self._actor.root, self._s_dirExtract)
        cmd_extract = (
                       'mkdir -p {0}; '
                       'tar -xzf {1} -C {0}; '
                       'rm {1};'
                      ).format(s_dstdirExtract, s_dstTar)
        self._actor.execRemoteCmdBlocking(cmd_extract)

def deployTarFileWrapper(tfd):
    tfd.deploy()

# Create a tarball of the files in ls_files
# - root is the directory in which ls_files should be found
# - s_tarName is the desired name of the tarball (gzipped!)
# - ls_files is a list of file paths, *relative to root*
# Returns local path of tarball
# Side Effect: creates new tarball, changes directory, changes back
def createTarFile_(root, s_tarName, ls_files):
    s_tarPath = os.path.join(root, s_tarName)
    olddir = os.getcwd()
    os.chdir(root)
    with tarfile.open(s_tarPath, 'w:gz') as tar:
        for f in ls_files:
            assert os.path.exists(f)
            tar.add(f)
    os.chdir(olddir)
    return s_tarPath

