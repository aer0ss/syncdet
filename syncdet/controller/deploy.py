#############################################################################
# Deployment Functions:
# - to deploy actor case source code to actors
# - to deploy test case source and scenarios to actors
# - to collect log files from actors to the controller's system
#############################################################################
import os.path

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

# Deploys the "case/actor" package source code files
# to all known Systems
# - assumes all files in ACTOR_PY_FILES exist locally
def deployActorSrc(verbose):
    if not config.DIRECTORY_SHARING:
        s_locRoot = lib.getLocalRoot()
    
        # Iterate over the number of systems
        for system in systems.systems:
            assert isinstance(system, systems.System)
            s_dstRoot = system.detRoot
            
            # Ensure the destination DET root and case directories
            # are present on the remote machine.
            cmd_mkdir = 'mkdir -p %s/case' % (s_dstRoot)
            system.executeRemoteCmd(os.P_WAIT, cmd_mkdir, verbose)
    
            for f in ACTOR_PY_FILES:
                s_locPath = os.path.join(s_locRoot, f)
                assert os.path.exists(s_locPath)
                s_dstPath = os.path.join(s_dstRoot, f)
                system.copyTo(s_locPath, s_dstPath)


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
        
