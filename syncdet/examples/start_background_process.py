'''This test case demonstrates how to start a background (daemon) process.'''

from case import startBackgroundProcess

def default():
    startBackgroundProcess(['sleep', '123456'])
spec = { 'default': default }
