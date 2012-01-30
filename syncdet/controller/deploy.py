#############################################################################
# Deployment Functions:
# - to deploy actor case source code to actors
# - to deploy test case source and scenarios to actors
# - to collect log files from actors to the controller's system
#############################################################################
from multiprocessing import Pool
import os.path, os, tarfile

import lib, log
import config, systems

# Tuple of src files which must be deployed for actors to run cases
# - file path relative to syncdet root
ACTOR_PY_FILES =     ( 'systems.py', 'config.py', 'systemsdef.py',
                       'case/syncdet_actor_wrapper.py', 
                       'case/syncdet_case_lib.py',
                       'case/syncdet_case_sync.py',
                       'case/__init__.py',
                      )
ACTOR_TAR_PATH = 'actorsrc.tar.gz'

# Deploys the "case/actor" package source code files
# to all known Systems
# - assumes all files in ACTOR_PY_FILES exist locally
def deployActorSrc():
    if not config.DIRECTORY_SHARING:
        s_locRoot = lib.getLocalRoot()

        # Create a tarball of Actor source files
        s_tarPath = createTarFile_(s_locRoot, ACTOR_TAR_PATH, ACTOR_PY_FILES)

        # For each system, scp the tar file and extract it
        p = Pool(lib.getSysCount())
        p.map(deployTarFileWrapper, 
               [TarFileDeployer(s_tarPath, '', syst) for syst in systems.systems])

        # Done with the tar file; locally remove it
        if os.path.exists(s_tarPath): os.remove(s_tarPath)


# Deploys the test case directory of source files to the specified systems
# - relTestDir is relative to SyncDET root directory
CASE_TAR_PATH = 'casesrc.tar.gz'
def deployCaseSrc(s_relTestDir, ls_systems):
    assert len(ls_systems) > 0
    if not config.DIRECTORY_SHARING:
        s_tarPath = createTarFile_(lib.getLocalRoot(), 
                                    CASE_TAR_PATH, [s_relTestDir])
    
        # For each system, scp the tar file and extract it
        p = Pool(len(ls_systems))
        p.map(deployTarFileWrapper, 
               [TarFileDeployer(s_tarPath, os.path.dirname(s_relTestDir), syst) 
                for syst in ls_systems])

        # Done with the tar file; locally remove it
        if os.path.exists(s_tarPath): os.remove(s_tarPath)


def gatherLog(sysId, module, instId):
    if not config.DIRECTORY_SHARING:

        system = systems.getSystem(sysId)

        # Determine where the logfile should be stored locally
        s_locLogPath = log.getLocalLogPath(sysId, module, instId)

        # The remote file name should be the same, needing only account for
        # a different SyncDET root
        s_remLogPath = s_locLogPath.replace(
                            lib.getLocalRoot(),
                            system.detRoot)

        # TODO: - handle remote does not have file
        #       - handle local can not store file
        system.copyFrom(s_remLogPath, s_locLogPath)
        

############################################################
# Local helper functions and classes
############################################################

#class SourceCodeDeployer:
#    _systems = []

class TarFileDeployer:
    _s_locTar = ''
    # Directory to extract the tarball, relative to SyncDET root
    _s_dirExtract = '' 
    _system = None
    def __init__(self, s_locTar, s_dirExtract, system):
        self._s_locTar = s_locTar
        self._s_dirExtract = s_dirExtract
        self._system = system
        assert os.path.exists(self._s_locTar)
        assert isinstance(self._system, systems.System)

    def deploy(self):
        
        # Copy over the tar file to the home directory
        s_dstTar = os.path.join('~', os.path.basename(self._s_locTar))
        self._system.copyTo(self._s_locTar, s_dstTar)

        # Ensure the destination extraction directory exists
        # Then extract the tar file to that directory and remove the tar
        s_dstdirExtract = os.path.join(self._system.detRoot, self._s_dirExtract)
        cmd_extract = (
                       'mkdir -p {0}; '
                       'tar -xzf {1} -C {0}; '
                       'rm {1};'
                      ).format(s_dstdirExtract, s_dstTar)
        self._system.executeRemoteCmd(os.P_WAIT, cmd_extract)

def deployTarFileWrapper(tfd):
    tfd.deploy()


# Create a tarball of the files in ls_files
# - s_detRoot is the SyncDET Root
# - s_tarName is the desired name of the tarball (gzipped!)
# - ls_files is a list of file paths, *relative to s_detRoot*
# Returns local path of tarball
# Side Effect: creates new tarball, changes directory, changes back
def createTarFile_(s_detRoot, s_tarName, ls_files):
    s_tarPath = os.path.join(s_detRoot, s_tarName)
    olddir = os.getcwd()
    os.chdir(s_detRoot)
    with tarfile.open(s_tarPath, 'w:gz') as tar:
        for f in ls_files:
            assert os.path.exists(f)
            tar.add(f)
    os.chdir(olddir)
    return s_tarPath

