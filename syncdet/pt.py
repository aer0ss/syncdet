#!/usr/bin/python

import sys, os

import systems, config

def walk():
    cmd = ''
    for i in sys.argv[2:]: cmd += i + ' '
    for i in range(len(systems.systems)):
        system = systems.systems[i]
        args = [
               system['rsh'],
               system['login'] + '@' + system['address'],
               cmd
               ]
        print '==============', system['address'], '================'
        os.spawnvp(os.P_WAIT, args[0], args)

##########################################################

def usage():
    print 'py: SyncDET PowerTools'
    print 
    print '    %s <tool> [<options>]' % sys.argv[0]
    print
    print 'TOOLS:'
    print '    walk <cmd>: run <cmd> on each system'
    print
    
    sys.exit()    

if len(sys.argv) < 2: usage()

if sys.argv[1] == 'walk': walk()
else: usage()

