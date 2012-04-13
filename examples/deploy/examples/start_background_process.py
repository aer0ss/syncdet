"""
This test case demonstrates how to start a background (daemon) process.
"""

from syncdet.case import background

def default():
    background.start_process(['sleep', '123456'])
spec = { 'default': default }
