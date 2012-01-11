#
# The Syncdet system definition file
#     Contains the accessor for a particular system,
#     definition of the System class
#
# To view or change attributes of particular systems, see systemsdef.py
import os
import systemsdef

# Global definition of list of systems
systems = [];

def getSystem(sysId):
    return systems[sysId]

# Class definition of a System
class System:
    rsh = ''
    login = ''
    detRoot = ''
    address = ''
    _copyFrom = 'scp -r %login@%host:%src %dst'
    _copyTo   = 'scp -r %src %login@%host:%dst'

    def __init__(self, d_system):
        assert isinstance(d_system, dict)

        for elem in d_system.keys():
            self.__dict__[elem] = d_system[elem]

        self._copyFrom, self._copyTo = (
            s.replace('%host', self.address).replace('%login', self.login)
             for s in (self._copyFrom, self._copyTo)
            )

    def copyFrom(self, src, dst):
        cmd = self._copyFrom
        self._copy(cmd, src, dst)

    def copyTo(self, src, dst):
        cmd = self._copyTo
        self._copy(cmd, src, dst)

    # return the result of os.spawnvp, according to mode. cmd is a string
    #
    def executeRemoteCmd(self, mode, cmd, verbose):
        args = [
               self.rsh,
               self.login + '@' + self.address,
               cmd
               ]
        if verbose:
            print 'cmd[%d]' % systems.index(self),
            for arg in args: print arg,
            print 
        return os.spawnvp(mode, args[0], args)

        
    def _copy(self, cmd, src, dst):
        cmd = cmd.replace('%src', src)
        cmd = cmd.replace('%dst', dst)
        print cmd
        os.system(cmd)


# Static initialization from systemsdef.py
for d_system in systemsdef.d_systems:
    systems.append(System(d_system))
