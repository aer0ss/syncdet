#
# The SyncDET system definition file.
#    Define the computers to run the test and their attributes 
#
# one system must have at least the following attributes. More custom attributes
# can be defined and be retreived by case modules through case.getSystem() or 
# getLocalSystem()
#
# rsh:         the command to remotely login the system. we will use the 
#              following format to invoke commands on the remote system:
#                  rsh login@address <command_line>
#              Hence, user must ensure that the system can be logged on without
#              providing a password, and the above format can work properly.
#              Use 'rsh login@address ls -l' to test if it works.
#
# login:       the login name of the system. It should normally be the root.
#
# address:     the address or the host name of the system
#
# detRoot:     the directory will det should be copied over
# 
# copyFrom:    the command to copy a file %src on a remote host %host to a 
#              local path %dst. Must support directory copy and follow
#              symbol links if any.
#
# copyTo:      the command to copy a local file %src to %dst on a remote host 
#              %host. Must support directory copy and follow
#              symbol links if any.
#

defaults = {
           'rsh':     'ssh',
           'login':   'root',
           'detRoot': '/s/syncdet',
           'copyFrom': 'scp -r root@%host:%src %dst',
           'copyTo':   'scp -r %src root@%host:%dst',
           }

# the definition of the systems
systems = [
           { 'address': '192.168.195.130' },
           { 'address': '192.168.195.132' },
           { 'address': '192.168.195.133' },
           ]
           
# fill in the defaults
for system in systems:
    for attr in defaults.keys():
        if attr not in system.keys(): system[attr] = defaults[attr] 
