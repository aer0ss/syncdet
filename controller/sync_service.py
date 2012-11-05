# the synchronization service
#
# we choose to use TCP as opposed to UDP because the testing network
# might be using WAN simulation
#
#
# Request Data format:
#
#  "len S module.sig.syncId actorId vote timeout actorId1,actorId2...actorIdN"
#
#    len:      message length, NOT including itself
#    S:        the character 'S'
#    module:   case module name
#    sig:      instance signature
#    syncId:   the synchronizer Id within the test case.
#              caseName and syncId uniquely identify a synchronizer
#    actorId:    the actor Id identifying the sending host
#    vote:     'y' or 'n'
#    timeout:  the timeout value. counting starts from the time the
#              message is received. present but ignored when vote = 'n'.
#              0: use the default timeout (param.SYNC_TIMEOUT)
#    actorIdi:   the actor Ids the test case want to synchronize with.
#              present but ignored when vote = 'n'
#
#  "len C sig"
#
#    cancel all synchronizers belonging to the instance identified by sig.
#    when sig == 'all', cancel all synchronizers
#
# Reply Data Format (cancel requests do not have replies):
#
#  "len module.sig.syncId result"
#
#    len:      message length, NOT including itself
#    module:   case module name
#    sig:      instance signature
#    syncId:   the synchronizer Id within the test case
#    result:   'OK' or 'DENIED' or 'TIMEOUT'
#

#
# the only two functions the controller can call is startService() and
# cancel() as the sync service runs in another thread
#

import socket, select, threading, string
from deploy.syncdet import param, config

from synchronizer import process_timeout, process_request

def start_service(verbose):
    sListen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow service to rebind the socket quickly when restarted after crash or ^C
    sListen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sListen.bind(('', param.SYNC_SERVICE_PORT))
    sListen.listen(param.SYNC_SERVICE_BACKLOG)

    sListen.setblocking(0)

    svc = ThdSyncService(sListen, verbose)
    svc.start()

class ThdSyncService(threading.Thread):
    _listen = None
    _verbose = None

    def __init__(self, listen, verbose):
        threading.Thread.__init__(self)
        self._listen = listen
        self._verbose = verbose;

        self.setDaemon(True)

    def run(self):
        ssRead = [self._listen]
        while 1:
            ssIn, _, _ = select.select(ssRead, (), (), 1)

            # time out
            if not ssIn: process_timeout()

            # process socket input
            for s in ssIn:
                # accept a new connection
                if s is self._listen:
                    snew, _ = self._listen.accept()
                    snew.setblocking(0)
                    ssRead += [snew]
                else:
                    data = s.recv(1024)
                    if len(data):
                        parse_packet(s, data, self._verbose)
                    else:
                        s.close()
                        fini_socket(s)
                        ssRead.remove(s)

# stores data buffers that are incomplete. indexed by sockets
s_pendings = {}

def parse_packet(socket, data, verbose):
    global s_pendings
    # complete the buffer if we have data previously received
    if socket in s_pendings.keys():
        s_pendings[socket] += data
        data = s_pendings[socket]
    fields = string.split(data)
    # if we didn't get the whole 'len' field yet
    if len(fields) < 2:
        s_pendings[socket] = data
        return
    # data has insufficient length
    length = int(fields[0]) + len(fields[0])
    if len(data) < length:
        s_pendings[socket] = data
        return
    # cut off unused data if any
    if len(data) > length:
        s_pendings[socket] = data[length:]
        fields = string.split(data[:length])
    if verbose: print 'sync request:', fields
    process_request(socket, fields)

def fini_socket(socket):
    global s_pendings
    if socket in s_pendings: del s_pendings[socket]

def cancel_synchronizers(signature = 'all'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((param.SYNC_SERVICE_ADDRESS, param.SYNC_SERVICE_PORT))

    data = " C %s" % signature
    s.send("%d%s" % (len(data), data))

