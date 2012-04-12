"""
This test case demonstrates how to stop a background (daemon) process
launched by background.startProcess().
"""

from syncdet.case import background

def default():
    background.stopProcess('sleep')
spec = { 'default': default }
