import string
import socket
import struct
import time

from deploy.syncdet import param

# NOTE: we need to store the socket per request but not per actor because
#       an actor may fire multiple requests by multiple concurrent test cases

s_syncs = {}    # all pending synchronizers. { id: Synchronizer }


def _handle_cancel(socket, id):
    global s_syncs
    if id == 'all':
        s_syncs = {}
    else:
        for syncId in s_syncs:
            if syncId.find(id) >= 0: del s_syncs[syncId]


def _handle_sync(socket, id, actor, vote, timeout, waits):
    global s_syncs

    actor = int(actor)
    vote = 1 if vote == 'y' else 0
    timeout = int(timeout)
    waits = map(lambda s: int(s), string.split(waits, ','))

    # create the synchronizer if not exists
    if id not in s_syncs:
        s_syncs[id] = Synchronizer(id)

    s_syncs[id].add_participant(socket, actor, vote, timeout, waits)
    if s_syncs[id].is_done():
        del s_syncs[id]


def process_timeout():
    global s_syncs
    now = time.time()
    for id in s_syncs:
        s_syncs[id].check_timeout(now)
        if s_syncs[id].is_done(): del s_syncs[id]


# TODO: avoid globals
s_sync_ng = {}

_VOTE_FMT = "<HH"
_VOTE_SIZE = struct.calcsize(_VOTE_FMT)

OK = 0
BAD_ARGS = 1
CONFLICT = 2


def _handle_get(socket, id):
    global s_sync_ng

    votes = s_sync_ng.get(id, {})
    data = struct.pack("<I", len(votes) * _VOTE_SIZE)

    for actor, vote in votes.iteritems():
        data += struct.pack(_VOTE_FMT, actor, vote)

    socket.send(data)


def _handle_post(socket, id, actor, vote):
    global s_sync_ng

    #print "recvd vote {0} {1} {2}".format(id, actor, vote)
    actor = int(actor)
    vote = int(vote)

    if not (0 <= actor <= 65535 and 0 <= vote <= 65535):
        _send_code(socket, BAD_ARGS)
        return

    if id not in s_sync_ng:
        s_sync_ng[id] = {}

    votes = s_sync_ng[id]

    if actor in votes:
        _send_code(socket, CONFLICT)
        return

    votes[actor] = vote
    _send_code(socket, OK)


def _send_code(socket, code):
    socket.send(struct.pack("<H", code))


req_handlers = {
    'C': _handle_cancel,
    'S': _handle_sync,
    'G': _handle_get,
    'P': _handle_post
}


# fields[0]: length
# fields[1]: S or C
def process_request(socket, fields):
    type = fields[1]

    try:
        h = req_handlers[type]
    except KeyError:
        print "invalid sync request: %s" % type
        return

    h(socket, *fields[2:])


class Synchronizer:

    @staticmethod
    def OK():
        return

    @staticmethod
    def DENIED():
        return

    @staticmethod
    def TIMEOUT():
        return

    part = {}    # current participants: { actorId : socket }
    expect = []  # expected participants: [ actorId ]
    id = ''
    result = OK
    timeout = 0

    def __init__(self, id):
        self.id = id
        self.part = {}
        self.expect = []
        self.result = self.OK
        self.timeout = 0

    # vote: 1 yes, 0 no
    def add_participant(self, socket, actorId, vote, timeout, waits):
        # remove from expected
        if actorId in self.expect: self.expect.remove(actorId)

        # add as participant
        assert actorId not in self.part.keys(), \
            "actor %d already requested '%s'" % (actorId, self.id)
        self.part[actorId] = socket

        # add the waits that are not participants as expected
        for wait in waits:
            if wait not in self.part.keys() and wait not in self.expect:
                self.expect += [wait]

        if self.result == self.OK:
            if vote:
                if self.is_done():
                    # bingle !
                    self.reply_all_participants()
                else:
                    # recalculate timeout
                    if not timeout: timeout = param.SYNC_TIMEOUT
                    if not self.timeout or time.time() + timeout < self.timeout:
                        self.timeout = time.time() + timeout
            else:
                # darn. the sync denied
                self.result = self.DENIED
                self.reply_all_participants()
        else:
            # sync has already failed. reply non-OK
            self.reply(actorId)

    # are we done (i.e. the object can be deleted) ?
    def is_done(self): return not len(self.expect)

    def check_timeout(self, now):
        if self.result != self.OK or now < self.timeout: return
        self.result = self.TIMEOUT
        self.reply_all_participants()

    def reply(self, actorId):
        if not self.part[actorId]: return

        if self.result == self.OK: m = 'OK'
        elif self.result == self.DENIED: m = 'DENIED'
        else: m = 'TIMEOUT'
        data = " %s %s" % (self.id, m)

        try:
            self.part[actorId].send("{0}{1}".format(len(data), data))
        except socket.error as e:
            if e.errno == socket.errno.EBADF:
                print "socket to actor {0} was lost".format(actorId)
            else:
                raise e
        # can send only one reply per participant
        self.part[actorId] = None

    def reply_all_participants(self):
        for actorId in self.part.keys(): self.reply(actorId)
