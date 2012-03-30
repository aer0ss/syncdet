import string, time

import config

# NOTE: we need to store the socket per request but not per actor because 
#       a actor may fire multiple requests by multiple concurrent test cases

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
def processRequest(socket, fields):
    # identifier or sig
    id = fields[2]
    
    # type
    type = fields[1]
    assert type == 'S' or type == 'C'
    if type == 'C':
        processCancelRequest(id)
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
        processSyncRequest(socket, id, actorId, vote, timeout, waits)

def processCancelRequest(id):
    global s_syncs
    if id == 'all': 
        s_syncs = {}
    else:
        for syncId in s_syncs.keys():
            if syncId.find(id) >= 0: del s_syncs[syncId]

def processSyncRequest(socket, id, actorId, vote, timeout, waits):
    global s_syncs
    # create the synchronizer if not exists
    if id not in s_syncs.keys():
        s_syncs[id] = Synchronizer(id)

    s_syncs[id].addParticipant(socket, actorId, vote, timeout, waits)
    if s_syncs[id].isDone(): del s_syncs[id]

def processTimeOut():
    global s_syncs
    now = time.time()
    for id in s_syncs.keys():
        s_syncs[id].checkTimeOut(now)
        if s_syncs[id].isDone(): del s_syncs[id]
    
class Synchronizer:

    def OK(): return
    def DENIED(): return 
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
    def addParticipant(self, socket, actorId, vote, timeout, waits):            
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
                if self.isDone():
                    # bingle !
                    self.replyAllParticipants()
                else:
                    # recalculate timeout
                    if not timeout: timeout = config.SYNC_TIMEOUT
                    if not self.timeout or time.time() + timeout < self.timeout:
                        self.timeout = time.time() + timeout
            else:
                # darn. the sync denied
                self.result = self.DENIED
                self.replyAllParticipants()
        else:
            # sync has already failed. reply non-OK
            self.reply(actorId)
        
    # are we done (i.e. the object can be deleted) ?
    def isDone(self): return not len(self.expect)

    def checkTimeOut(self, now):
        if self.result != self.OK or now < self.timeout: return
        self.result = self.TIMEOUT
        self.replyAllParticipants()
    
    def reply(self, actorId):
        if not self.part[actorId]: return
        
        if self.result == self.OK: m = 'OK'
        elif self.result == self.DENIED: m = 'DENIED'
        else: m = 'TIMEOUT'
        data = " %s %s" % (self.id, m)

        self.part[actorId].send("%d%s" % (len(data), data))
        # can send only one reply per participant
        self.part[actorId] = None
    
    def replyAllParticipants(self):
        for actorId in self.part.keys(): self.reply(actorId)
