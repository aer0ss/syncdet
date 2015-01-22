import socket
import string
import struct
import time
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
def sync(id, waits=None, timeout=0, voteYes=True):
    if waits is None:
        # list all other actors
        waits = range(case.actor_id()) + range(case.actor_id() + 1, case.actor_count())
    if not waits:
        return

    v = '' if voteYes else 'DENY'
    print "SYNC '{0}' {1}".format(id, v)

    s = _send_request(_build_request(id, waits, voteYes, timeout))
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
def sync_prev(pnid, prev=None, timeout=0, voteYes=True):
    if prev is None:
        if case.actor_id() == 0: return case.OK
        else: prev = case.actor_id() - 1

    id = '{0}.{1}<=>{2}'.format(pnid, prev, case.actor_id())
    return sync(id, [prev], timeout, voteYes)


def sync_next(pnid, next=None, timeout=0, voteYes=True):
    if next is None:
        if case.actor_id() == case.actor_count() - 1: return case.OK
        else: next = case.actor_id() + 1

    id = '{0}.{1}<=>{2}'.format(pnid, case.actor_id(), next)
    return sync(id, [next], timeout, voteYes)


def _make_sync_id(id):
    # convert spaces to underscores because we use the former as the delimiter
    syncId = string.translate(str(id), string.maketrans(' ', '_'))
    return "{0}.{1}.{2}".format(case.module_name(),
                                case.instance_id(),
                                syncId)


#  request format:
#    "len S module.sig.syncId actorId vote timeout actorId1,actorId2...actorIdN"
# see controller/sync.py for detail
def _build_request(id, waits, v, to):
    vote = 'y' if v else 'n'
    timeout = to
    actorIds = ''
    for i in range(len(waits)):
        actorIds += str(waits[i])
        if i < len(waits) - 1:
            actorIds += ','
    return "S {0} {1} {2} {3} {4}".format(_make_sync_id(id), case.actor_id(), vote, timeout, actorIds)


# reply format
#   "len module.sig.syncId result"
# see controller/sync.py for detail
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


def _validator_all_1(votes):
    for actor in xrange(0, case.actor_count()):
        if actor not in votes or votes[actor] != 1:
            return False
    return True


# id        : string
# validator : ({actor: vote}) -> bool
# vote      : int16 or () -> int16
# delay     : float (seconds)
# timeout   : float (seconds)
def sync_ng(id, validator=_validator_all_1, vote=1, delay=0.2, timeout=param.SYNC_TIMEOUT):
    v = None
    voted = False

    print "sync-enter {0}".format(id)

    timeout_time = time.time() + timeout

    while True:
        if not voted:
            if v is None:
                #try:
                v = vote()
                #except:
                #    v = int(v)

            if v is not None:
                voted = _vote(id, v)

        if _check(id, validator):
            break

        if time.time() > timeout_time:
            raise ExSyncTimeout

        time.sleep(delay)

    print "sync-leave {0}".format(id)


def _vote(id, vote):
    assert (0 <= int(vote) <= 65535), "Invalid vote: %s" % vote
    print "vote {0} {1}".format(id, vote)
    s = _send_request("P {0} {1} {2}".format(_make_sync_id(id), case.actor_id(), int(vote)))

    data = s.recv(2)
    code = struct.unpack("<H", data)[0]
    assert code == 0, "Unexpected return code: %s" % code
    return True


def _check(id, validator):
    s = _send_request("G {0}".format(_make_sync_id(id)))

    data = s.recv(4)
    assert len(data) == 4, "Invalid response header: %s" % len(data)
    size = struct.unpack("<I", data)[0]
    assert size % 4 == 0, "Invalid response size: %s" % size

    buffer = ""
    while len(buffer) < size:
        buffer += s.recv(min(4096, size - len(buffer)))

    votes = {}
    for i in xrange(0, size, 4):
        actor, vote = struct.unpack("<HH", buffer[i:i+4])
        assert actor not in votes, "Multiple votes for actor %s" % actor
        votes[actor] = vote

    if len(votes) != 0:
        print "votes for %s : %s" % (id, votes)

    return validator(votes)


def _send_request(data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((param.SYNC_SERVICE_ADDRESS, param.SYNC_SERVICE_PORT))
    s.send("{0} {1}".format(len(data) + 1, data))
    return s
