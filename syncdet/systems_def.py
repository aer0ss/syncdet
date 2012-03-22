#
# The SyncDET system definition file.
#    Define the computers to run the test and their attributes 
#
# one system must have at least the following attributes. 
# NOTE: the following is not supported currently:
# More custom attributes can be defined and be retreived by case modules 
# through case.getSystem() or getLocalSystem()
#
# rsh:         the command to remotely login to the system. we will use the 
#              following format to invoke commands on the remote system:
#                  rsh login@address <command_line>
#              Hence, user must ensure that the system can be logged on without
#              providing a password, and the above format can work properly.
#              Use 'rsh login@address ls -l' to test if it works.
#
# login:       the login name of the system. It should normally be the root.
#
# detRoot:     the directory where det should be copied over
# 
# address:     the address or the host name of the system
#

defaults = {
           'rsh':     'ssh',
           'login':   'aerofstest',
           'detRoot': '~/atf/syncdet',
           }

# the dictionary definition of the systems
d_systems = [
           { 'address': '192.168.1.35' },
           { 'address': '192.168.1.37' },
           ]

# fill in the defaults
for d_system in d_systems:
    for attr in defaults.keys():
        if attr not in d_system.keys(): d_system[attr] = defaults[attr] 

