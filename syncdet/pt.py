#!/usr/bin/python

import sys, os

import actors

def walk():
    cmd = ''
    for i in sys.argv[2:]: cmd += i + ' '
    for i in range(len(actors.actors)):
        actor = actors.actors[i]
        args = [
               actor['rsh'],
               actor['login'] + '@' + actor['address'],
               cmd
               ]
        print '==============', actor['address'], '================'
        os.spawnvp(os.P_WAIT, args[0], args)

##########################################################

def usage():
    print 'py: SyncDET PowerTools'
    print
    print '    %s <tool> [<options>]' % sys.argv[0]
    print
    print 'TOOLS:'
    print '    walk <cmd>: run <cmd> on each actor'
    print

    sys.exit()

if len(sys.argv) < 2: usage()

if sys.argv[1] == 'walk': walk()
else: usage()

