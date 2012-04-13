"""
This test case demonstrates how to stop a background (daemon) process
launched by background.startProcess().
"""

from syncdet.case import background

def default():
    background.stop_process('sleep')
spec = { 'default': default }
