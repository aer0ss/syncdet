#
# The Syncdet actor definition file
#     Contains the accessor for a particular actor,
#     definition of the Actor class
#
# To view or change attributes of particular actors, see actorsdef.py
import os, sys, subprocess
import config
import param

# a list of Actor objects
_actors = []

def actor_list():
    return _actors

def actor_count():
    assert len(_actors) > 0
    return len(_actors)

def actor(actorId):
    return _actors[actorId]

# Initialize the global list of actors with
# - the max permissable number of actors
# - whether to display verbose msgs
#
def init(verbose, maxNumActors = None):
    global _actors
    # Static initialization from config.py
    for d_actor in config.get().actors:
        _actors.append(Actor(d_actor, verbose))

    if maxNumActors and maxNumActors < len(_actors):
        _actors = _actors[:maxNumActors]

# Class definition of a Actor
class Actor:
    rsh = ''
    rsh_remote_args = []
    login = ''
    root = ''
    address = ''
    os = ''
    _copy_from = ['scp', '-r', '%login@%host:%src', '%dst']
    _copy_to = ['scp', '-r', '%src', '%login@%host:%dst']
    _verbose = False # Verbose output?

    def __init__(self, d_actor, verbose):
        assert isinstance(d_actor, dict)
        self._verbose = verbose

        for elem in d_actor.keys():
            self.__dict__[elem] = d_actor[elem]

        self._copy_from, self._copy_to = (
               [s.replace('%host', self.address).replace('%login', self.login)
                 for s in copyList]
                 for copyList in (self._copy_from, self._copy_to)
            )

    def copy_from(self, src, dst):
        cmd = self._copy_from
        self._copy(cmd, src, dst)

    def copy_to(self, src, dst):
        cmd = self._copy_to
        self._copy(cmd, src, dst)

    def rsync(self, srcs, dst):
        """
        Rsync the src folder from the local system (the controller) to the
        dst folder on the actor, using rsync's option --relative. See rsync(1)
        for detail.
        @param srcs: the list of source folders on the controller
        @param dst: the destination folder on the actor
        """
        cmd = [
            'rsync',
            '--archive',
            '--compress',
            '--relative',
            '--copy-unsafe-links',
            '--exclude', '*.pyc', # exclude
            '--delete',
            '--delete-excluded',
            '--rsh', self.rsh, # login method
        ]

        # specify sources
        cmd.extend(srcs)

        # specify destination
        cmd.append(self.login + '@' + self.address + ':' + dst)

        try:
            self._run_local_cmd(cmd)
        except subprocess.CalledProcessError, _:
            self.exec_remote_cmd_blocking('mkdir -p ' + self.root)
            self._run_local_cmd(cmd)

    def exec_remote_cmd_blocking(self, cmd):
        """@param cmd: the string contains both the command to execute and its
        arguemts, e.g., 'ls -l'
        """
        return self._execute_remote_cmd(os.P_WAIT, cmd)

    # return the pid of the local proxy process. cmd is a string
    #
    def exec_remote_cmd_non_blocking(self, cmd):
        """@param cmd: the string contains both the command to execute and its
        arguemts, e.g., 'ls -l'
        """
        return self._execute_remote_cmd(os.P_NOWAIT, cmd)

    # return the result of os.spawnvp, according to mode. cmd is a string
    #
    def _execute_remote_cmd(self, mode, cmd):
        cmdLocal = [
               self.rsh,
               self.login + '@' + self.address,
               "-R{0}:localhost:{0}".format(param.SYNC_SERVICE_PORT)
               ] + self.rsh_remote_args + [
               cmd
               ]
        if self._verbose: print cmdLocal
        return os.spawnvp(mode, cmdLocal[0], cmdLocal)


    def _copy(self, cmd, src, dst):
        cmd = [s.replace('%src', src).replace('%dst', dst) for s in cmd]

        try:
            self._run_local_cmd(cmd)
        except subprocess.CalledProcessError, e:
            if self._verbose:
                s_warning = ('<Actor._copy> {0}'
                        'see http://support.attachmate.com/techdocs/2116.html'
                        ).format(e)
                print s_warning
                sys.exit(1)

    def _run_local_cmd(self, cmd):
        if self._verbose:
            print cmd
            subprocess.check_call(cmd)
        else:
            with open(os.devnull, 'w') as fnull:
                subprocess.check_call(cmd, stdout = fnull, stderr = fnull)
