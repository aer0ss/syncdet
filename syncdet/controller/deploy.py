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
               [TarFileDeployer(s_tarPath, syst) for syst in systems.systems])

        # Done with the tar file; locally remove it
        if os.path.exists(s_tarPath): os.remove(s_tarPath)


# Deploys the test case directory of source files to the specified system
# - relTestDir is relative to SyncDET root directory
CASE_TAR_PATH = 'casesrc.tar.gz'
def deployCaseSrc(s_relTestDir, system):
    if not config.DIRECTORY_SHARING:
        s_locDir, s_dstDir = (
                        os.path.normpath(os.path.join(root, s_relTestDir))
                        for root in (lib.getLocalRoot(), system.detRoot)
                              )
        assert os.path.exists(s_locDir)

        ls_fpy = [os.path.normpath(os.path.join(s_relTestDir, f)) 
                   for f in os.listdir(s_locDir) if os.path.splitext(f) != '.pyc']
        print ls_fpy
        #createTarFile(lib.getLocalRoot(), CASE_TAR_PATH, ls_fpy)
    
        # Ensure the destination test directory's parent is present
        cmd_mkdir = 'mkdir -p %s' % (s_dstDir)
        system.executeRemoteCmd(os.P_WAIT, cmd_mkdir)
    
        # Copy the entire test directory to the remote machine
        #   -copy the local directory to the parent of the destination
        system.copyTo(s_locDir, os.path.dirname(s_dstDir))

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
    _system = None
    def __init__(self, s_locTar, system):
        self._s_locTar = s_locTar
        self._system = system
        assert os.path.exists(self._s_locTar)
        assert isinstance(self._system, systems.System)

    def deploy(self):
        
        # Copy over the tar file to the home directory
        s_dstTar = os.path.join('~', os.path.basename(self._s_locTar))
        self._system.copyTo(self._s_locTar, s_dstTar)

        # Ensure the destination DET root and case directories
        # are present on the remote machine.
        # Then extract the tar file to the syncdet root and remove the tar
        s_dstRoot = self._system.detRoot
        cmd_extract = ('mkdir -p {0}; '
                       'tar -xzf {1} -C {0}; '
                       'rm {1};'
                      ).format(self._system.detRoot, s_dstTar)
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


