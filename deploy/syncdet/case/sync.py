import socket, string
from .. import param, config, case

class ExSyncFail(Exception):
    def __str__(self):
        return "SYNC FAILED"

class ExSyncTimeout(Exception):
    def __str__(self):
        return "SYNC TIMEOUT"

# id:      the sync id, can be either numerical or textual, identifying the
#          synchronizer within the scope of the instance
# voteYes: False: vote no. it will cause the synchronization to fail
# timeout: 0: use the default, system-wide timeout (param.SYNC_TIMEOUT)
# waits:   a list of actorId's to synchronize with. Passing None will
#          sync with ALL other instances
#
# raise:   ExSyncFail, ExSyncTimeout
#
def sync(id, waits = None, timeout = 0, voteYes = True):
    if waits == None:
        # list all other actors
        waits = range(case.actor_id()) + range(case.actor_id() + 1,
                case.actor_count())
    if not waits:
        return

    if voteYes: v = ''
    else:       v = 'DENY'
    print "SYNC '{0}' {1}".format(id, v)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((config.controllerAddress, param.SYNC_SERVICE_PORT))
    data = _build_request(id, waits, voteYes, timeout)
    s.send(data)
    # BUGBUG: we don't consider partial receiving now
    data = s.recv(4096)
    return _parse_reply(id, data)

# pnid: this param and prev in conjunction identify a sync id.
#       Therefore, sync_prev/next on the local actor won't mess up with other
#       actors with the same sync_prev/next id.
#
# prev/next: the previous or next actor to sync. passing None will sync
#       with the actor which actorId numerically precedes or succeed the local
#       actor, and if the local actorId is zero or getSysCount() - 1, return OK
#       immediately.
#
def sync_prev(pnid, prev = None, timeout = 0, voteYes = True):

    if prev == None:
        if case.actor_id() == 0: return case.OK
        else: prev = case.actor_id() - 1

    id = '{0}.{1}<=>{2}'.format(pnid, prev, case.actor_id())
    return sync(id, [prev], timeout, voteYes)

def sync_next(pnid, next = None, timeout = 0, voteYes = True):

    if next == None:
        if case.actor_id() == case.actor_count() - 1: return case.OK
        else: next = case.actor_id() + 1

    id = '{0}.{1}<=>{2}'.format(pnid, case.actor_id(), next)
    return sync(id, [next], timeout, voteYes)

def _make_sync_id(id):
    # convert spaces to underscores becuase we use the former as the delimiter
    syncId = string.translate(str(id), string.maketrans(' ', '_'))
    return "{0}.{1}.{2}".format(case.module_name(),
                                case.instance_id(),
                                syncId)

#  request format:
#    "len S module.sig.syncId actorId vote timeout actorId1,actorId2...actorIdN"
# see controller/sync.py for detail
#
def _build_request(id, waits, v, to):
    if v: vote = 'y'
    else: vote = 'n'
    timeout = to
    actorIds = ''
    for i in range(len(waits)):
        actorIds += str(waits[i])
        if i < len(waits) - 1: actorIds += ','
    data = " S {0} {1} {2} {3} {4}".format(_make_sync_id(id), case.actor_id(),
                                           vote, timeout, actorIds)
    return "{0}{1}".format(len(data), data)

# reply format
#   "len module.sig.syncId result"
# see controller/sync.py for detail
#
def _parse_reply(id, data):
    fields = string.split(data)
    assert len(fields) == 3
    assert int(fields[0]) == len(fields[1]) + len(fields[2]) + 2
    assert fields[1] == _make_sync_id(id)

    if fields[2] == 'OK':
        return
    elif fields[2] == 'DENIED':
        raise ExSyncFailed
    else:
        assert fields[2] == 'TIMEOUT'
        raise ExSyncTimeout
