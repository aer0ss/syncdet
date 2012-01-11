#############################################################################
# Deployment Functions:
# - to deploy actor case source code to actors
# - to deploy test case source and scenarios to actors
# - to collect log files from actors to the controller's system
#############################################################################
import os.path

import lib, controller
import config, systems

# Tuple of src files which must be deployed for actors to run cases
# - file path relative to syncdet root
ACTOR_PY_FILES =     ( 'systems.py', 'config.py', 'systemsdef.py',
                       'case/syncdet_actor_wrapper.py', 
                       'case/syncdet_case_lib.py',
                       'case/syncdet_case_sync.py',
                      )

# Deploys the source files in s_filePaths to all
# Systems in the list ls_systems
# - assumes all files in ACTOR_PY_FILES exist locally
def deployCaseSrc():
    s_srcRoot = lib.getLocalRoot()

    # Iterate over the number of systems
    for system in systems.systems:
        assert isinstance(system, systems.System)
        s_dstRoot = system.detRoot
        
        # Ensure the destination DET root and case directories
        # are present on the remote machine.
        cmd_mkdir = 'mkdir -p %s/case' % (s_dstRoot)
        system.executeRemoteCmd(os.P_WAIT, cmd_mkdir, True)

        for f in ACTOR_PY_FILES:
            s_srcPath = os.path.join(s_srcRoot, f)
            assert os.path.exists(s_srcPath)
            s_dstPath = os.path.join(s_dstRoot, f)
            system.copyTo(s_srcPath, s_dstPath)
