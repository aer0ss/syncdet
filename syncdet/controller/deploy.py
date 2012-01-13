#############################################################################
# Deployment Functions:
# - to deploy actor case source code to actors
# - to deploy test case source and scenarios to actors
# - to collect log files from actors to the controller's system
#############################################################################
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
def deployActorSrc(verbose):
    if not config.DIRECTORY_SHARING:
        s_locRoot = lib.getLocalRoot()

        # Create a tarball of Actor source files
        s_locTar = os.path.join(s_locRoot, ACTOR_TAR_PATH)
        olddir = os.getcwd()
        os.chdir(s_locRoot)
        with tarfile.open(s_locTar, 'w:gz') as tar:
            for f in ACTOR_PY_FILES:
                assert os.path.exists(f)
                tar.add(f)
        os.chdir(olddir)

        # Iterate over the systems, scp the tar file and extract it
        for system in systems.systems:
            assert isinstance(system, systems.System)
            s_dstRoot = system.detRoot
            
            # Ensure the destination DET root and case directories
            # are present on the remote machine.
            cmd_mkdir = 'mkdir -p {}'.format(s_dstRoot)
            system.executeRemoteCmd(os.P_WAIT, cmd_mkdir, verbose)

            # Copy over the tar file
            s_dstTar = os.path.join(s_dstRoot, ACTOR_TAR_PATH)
            system.copyTo(s_locTar, s_dstTar)

            # Extract the tar file to the syncdet root and remove the tar
            cmd_extract = ('tar -xzf {0} -C {1}; '
                           'rm {0};'
                          ).format(s_dstTar, s_dstRoot)
            system.executeRemoteCmd(os.P_WAIT, cmd_extract, verbose)
    

        # Done with the tar file; locally remove it
        if os.path.exists(s_locTar): os.remove(s_locTar)


# Deploys the test case directory of source files to the specified system
# - relTestDir is relative to SyncDET root directory
def deployCaseSrc(s_relTestDir, system, verbose):
    if not config.DIRECTORY_SHARING:
        s_locDir, s_dstDir = (
                        os.path.normpath(os.path.join(root, s_relTestDir))
                        for root in (lib.getLocalRoot(), system.detRoot)
                              )
        assert os.path.exists(s_locDir)
    
        # Ensure the destination test directory's parent is present
        cmd_mkdir = 'mkdir -p %s' % (s_dstDir)
        system.executeRemoteCmd(os.P_WAIT, cmd_mkdir, verbose)
    
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
        
