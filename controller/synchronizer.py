import string, time, socket

from deploy.syncdet import param

# NOTE: we need to store the socket per request but not per actor because
#       an actor may fire multiple requests by multiple concurrent test cases

s_syncs = {}    # all pending synchronizers. { id: Synchronizer }

#
# fields[0]: length
# fields[1]: S or C
# fields[2]: module.sig.syncId or sig
# fields[3]: the actorId
# fields[4]: vote
# fields[5]: timeout
# fields[6]: actorId1,actorId2...actorIdN
#
def process_request(socket, fields):
    # identifier or sig
    id = fields[2]

    # type
    type = fields[1]
    assert type == 'S' or type == 'C'
    if type == 'C':
        process_cancel_request(id)
    else:
        # actorId
        actorId = int(fields[3])
        # determin the vote
        if fields[4] == 'y': vote = 1
        else: vote = 0
        # timeout
        timeout = int(fields[5])
        # build the wait list
        fieldsWait = string.split(fields[6], ',')
        waits = []
        for wait in fieldsWait: waits.append(int(wait))
        process_sync_request(socket, id, actorId, vote, timeout, waits)

def process_cancel_request(id):
    global s_syncs
    if id == 'all':
        s_syncs = {}
    else:
        for syncId in s_syncs.keys():
            if syncId.find(id) >= 0: del s_syncs[syncId]

def process_sync_request(socket, id, actorId, vote, timeout, waits):
    global s_syncs
    # create the synchronizer if not exists
    if id not in s_syncs.keys():
        s_syncs[id] = Synchronizer(id)

    s_syncs[id].add_participant(socket, actorId, vote, timeout, waits)
    if s_syncs[id].is_done(): del s_syncs[id]

def process_timeout():
    global s_syncs
    now = time.time()
    for id in s_syncs.keys():
        s_syncs[id].check_timeout(now)
        if s_syncs[id].is_done(): del s_syncs[id]

class Synchronizer:

    @staticmethod
    def OK(): return
    @staticmethod
    def DENIED(): return
    @staticmethod
    def TIMEOUT(): return

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
