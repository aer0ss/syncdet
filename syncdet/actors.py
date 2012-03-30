#
# The Syncdet actor definition file
#     Contains the accessor for a particular actor,
#     definition of the Actor class
#
# To view or change attributes of particular actors, see actorsdef.py
import os, sys, subprocess
import actors_def

# Global definition of list of actors
actors = [];

def getActors():
    return actors

def getActorCount():
    assert len(actors) > 0
    return len(actors)

def getActor(actorId):
    return actors[actorId]

# Initialize the global list of actors with 
# - the max permissable number of actors
# - whether to display verbose msgs
#
def init(verbose, maxNumActors = None):
    global actors
    # Static initialization from actors_def.py
    for d_actor in actors_def.d_actors:
        actors.append(Actor(d_actor, verbose))

    if maxNumActors and maxNumActors < len(actors):
        actors = actors[:maxNumActors]

# Class definition of a Actor
class Actor:
    rsh = ''
    login = ''
    detRoot = ''
    address = ''
    _copyFrom = ['scp', '-r', '%login@%host:%src', '%dst']
    _copyTo = ['scp', '-r', '%src', '%login@%host:%dst']
    _verbose = False # Verbose output?

    def __init__(self, d_actor, verbose):
        assert isinstance(d_actor, dict)
        self._verbose = verbose

        for elem in d_actor.keys():
            self.__dict__[elem] = d_actor[elem]

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

    def execRemoteCmdBlocking(self, cmd):
        '''@param cmd: the string contains both the command to execute and its
        arguemts, e.g., 'ls -l'
        '''
        return self._executeRemoteCmd(os.P_WAIT, cmd)

    # return the pid of the local proxy process. cmd is a string
    #
    def execRemoteCmdNonBlocking(self, cmd):
        '''@param cmd: the string contains both the command to execute and its
        arguemts, e.g., 'ls -l'
        '''
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
                s_warning = ('<Actor._copy> {0}'
                             'see http://support.attachmate.com/techdocs/2116.html'
                            ).format(e)
                print s_warning
                sys.exit(-1)

