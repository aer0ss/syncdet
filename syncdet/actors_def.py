#
# The SyncDET actor definition file.
#    Define the computers to run the test and their attributes 
#
# one actor must have at least the following attributes. 
# NOTE: the following is not supported currently:
# More custom attributes can be defined and be retreived by case modules 
# through case.getActor() or getLocalActor()
#
# rsh:         the command to remotely login to the actor. we will use the 
#              following format to invoke commands on the remote actor:
#                  rsh login@address <command_line>
#              Hence, user must ensure that the actor can be logged on without
#              providing a password, and the above format can work properly.
#              Use 'rsh login@address ls -l' to test if it works.
#
# login:       the login name of the actor. It should normally be the root.
#
# detRoot:     the directory where det should be copied over
# 
# address:     the address or the host name of the actor
#

defaults = {
           'rsh':     'ssh',
           'login':   'aerofstest',
           'detRoot': '~/atf/syncdet',
           }

# the dictionary definition of the actors
d_actors = [
           { 'address': '192.168.1.103' },
           { 'address': '192.168.1.108' },
           ]

# fill in the defaults
for actor in d_actors:
    for attr in defaults.keys():
        if attr not in actor.keys(): actor[attr] = defaults[attr]

