import socket, string
import config

from syncdet_case_lib import getActorId, getActorCount, getInstanceId
from syncdet_case_lib import getCaseModuleName, OK, FAIL, TIMEOUT

# id:      the sync id, can be either numerical or textual, identifying the 
#          synchronizer within the scope of the instance
# voteYes: False: vote no. it will cause the synchronization to fail
# timeout: 0: use the default, system-wide timeout (config.SYNC_TIMEOUT)
# waits:   a list of actorId's to synchronize with. Passing None will
#          sync with ALL other instances
#
# return:  OK, FAIL, or TIMEOUT
#
def sync(id, waits = None, timeout = 0, voteYes = True):

    if waits == None:
        # list all other actors
        waits = range(getActorId()) + range(getActorId() + 1,
                getActorCount())
    if not waits:
        return OK

    if voteYes: v = ''
    else:       v = 'DENY'
    print "SYNC '%s' %s" % (str(id), v)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((config.CONTROLLER_ADDR, config.SYNC_SERVICE_PORT))
    data = buildRequest(id, waits, voteYes, timeout)
    s.send(data)
    # BUGBUG: we don't consider partial receiving now
    data = s.recv(4096)
    return parseReply(id, data)

# pnid: this param and prev in conjunction identify a sync id.
#       Therefore, syncPrev/Next on the local actor won't mess up with other
#       actors with the same syncPrev/Next id.
#
# prev/next: the previous or next actor to sync. passing None will sync 
#       with the actor which actorId numerically precedes or succeed the local 
#       actor, and if the local actorId is zero or getSysCount() - 1, return OK 
#       immediately 
#
def syncPrev(pnid, prev = None, timeout = 0, voteYes = True):

    if prev == None:
        if getActorId() == 0: return OK
        else: prev = getActorId() - 1

    id = '{0}.{1}<=>{2}'.format(pnid, prev, getActorId())
    return sync(id, [prev], timeout, voteYes)

def syncNext(pnid, next = None, timeout = 0, voteYes = True):

    if next == None:
        if getActorId() == getActorCount() - 1: return OK
        else: next = getActorId() + 1

    id = '{0}.{1}<=>{2}'.format(pnid, getActorId(), next)
    return sync(id, [next], timeout, voteYes)

def makeSyncId(id):
    # convert spaces to underscores becuase we use the former as the delimiter
    syncId = string.translate(str(id), string.maketrans(' ', '_'))
    return "%s.%s.%s" % (getCaseModuleName(), getInstanceId(), syncId)

#  request format:
#    "len S module.sig.syncId actorId vote timeout actorId1,actorId2...actorIdN"
# see controller/sync.py for detail
#
def buildRequest(id, waits, v, to):
    if v: vote = 'y'
    else: vote = 'n'
    timeout = to
    actorIds = '';
    for i in range(len(waits)):
        actorIds += str(waits[i])
        if i < len(waits) - 1: actorIds += ','
    data = " S %s %s %s %d %s" % (makeSyncId(id), getActorId(),
                                  vote, timeout, actorIds)
    return "%d%s" % (len(data), data)

# reply format
#   "len module.sig.syncId result"
# see controller/sync.py for detail
#
def parseReply(id, data):
    fields = string.split(data)
    assert len(fields) == 3
    assert int(fields[0]) == len(fields[1]) + len(fields[2]) + 2
    assert fields[1] == makeSyncId(id)

    if fields[2] == 'OK':
        return OK
    elif fields[2] == 'DENIED':
        print "SYNC FAILED"
        return FAIL
    else:
        assert fields[2] == 'TIMEOUT'
        print "SYNC TIMEOUT"
        return TIMEOUT
