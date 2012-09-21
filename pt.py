#!/usr/bin/env python

import sys
import os
import optparse

from deploy.syncdet import actors, config

def walk(walk_args):
    actors.init(False)
    cmd = ' '.join(walk_args)
    for actor in actors.actor_list():
        args = [
               actor.rsh,
               actor.login + '@' + actor.address,
               cmd
               ]
        print '==============', actor.address, '================'
        os.spawnvp(os.P_WAIT, args[0], args)

##########################################################

if __name__ == '__main__':
    usage_str = ('py: SyncDET PowerTools\n'
                '    {} [option] <tool> [<args>]\n'
                '\n'
                'TOOLS:\n'
                '    walk <cmd>: run <cmd> on each actor').format(sys.argv[0])

    parser = optparse.OptionParser(usage_str)

    parser.add_option('--config', dest='config',
                      help = 'the YAML configuration file to use. Defaults to '\
                      '/etc/syncdet/config.yaml',
                      default = '/etc/syncdet/config.yaml')

    options, args = parser.parse_args()

    try:
        config.load(os.path.expanduser(options.config))
    except IOError as e:
        # For prettier errors relating to missing config file
        print e
        sys.exit(1)

    if len(args) < 1:
        print usage_str
        sys.exit(1)

    if args[0] == 'walk':
        walk(args[1:])
    else:
        print usage_str
        sys.exit(1)
