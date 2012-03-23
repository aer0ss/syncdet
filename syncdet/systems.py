#
# The Syncdet system definition file
#     Contains the accessor for a particular system,
#     definition of the System class
#
# To view or change attributes of particular systems, see systemsdef.py
import os, sys, subprocess
import systems_def

# Global definition of list of systems
systems = [];

def getSystem(sysId):
    return systems[sysId]

# Initialize the global list of systems with 
# - the max permissable number of systems
# - whether to display verbose msgs
#
def init(verbose, maxNumSystems = None):
    global systems
    # Static initialization from systems_def.py
    for d_system in systems_def.d_systems:
        systems.append(System(d_system, verbose))

    if maxNumSystems and maxNumSystems < len(systems):
        systems = systems[:maxNumSystems]

# Class definition of a System
class System:
    rsh = ''
    login = ''
    detRoot = ''
    address = ''
    _copyFrom = ['scp', '-r', '%login@%host:%src', '%dst']
    _copyTo = ['scp', '-r', '%src', '%login@%host:%dst']
    _verbose = False # Verbose output?

    def __init__(self, d_system, verbose):
        assert isinstance(d_system, dict)
        self._verbose = verbose

        for elem in d_system.keys():
            self.__dict__[elem] = d_system[elem]

        self._copyFrom, self._copyTo = (
               [s.replace('%host', self.address).replace('%login', self.login)
                 for s in copyList]
                 for copyList in (self._copyFrom, self._copyTo)
            )

    def copyFrom(self, src, dst):
        cmd = self._copyFrom
        self._copy(cmd, src, dst)

    def copyTo(self, src, dst):
        cmd = self._copyTo
        self._copy(cmd, src, dst)

    def execRemoteCmdBlock(self, cmd):
        return self._executeRemoteCmd(os.P_WAIT, cmd)

    # return the pid of the local proxy process. cmd is a string
    #
    def execRemoteCmdNonBlock(self, cmd):
        return self._executeRemoteCmd(os.P_NOWAIT, cmd)

    # return the result of os.spawnvp, according to mode. cmd is a string
    #
    def _executeRemoteCmd(self, mode, cmd):
        args = [
               self.rsh,
               self.login + '@' + self.address,
               cmd
               ]
        if self._verbose:
            print 'cmd[{}]'.format(self.address),
            for arg in args: print arg,
            print
        return os.spawnvp(mode, args[0], args)


    def _copy(self, cmd, src, dst):
        cmd = [s.replace('%src', src).replace('%dst', dst) for s in cmd]

        try:
            if self._verbose:
                print ' '.join(cmd)
                subprocess.check_call(cmd)
            else:
                with open(os.devnull, 'w') as fstdout:
                    subprocess.check_call(cmd, stdout = fstdout)
        except subprocess.CalledProcessError, e:
            if self._verbose:
                s_warning = ('<System._copy> {0}'
                             'see http://support.attachmate.com/techdocs/2116.html'
                            ).format(e)
                print s_warning
                sys.exit(-1)

