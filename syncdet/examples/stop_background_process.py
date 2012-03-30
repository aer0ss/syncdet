'''This test case demonstrates how to stop a background (daemon) process 
launched by case.startBackgroundProcess().'''

from case import stopBackgroundProcess

def default():
    stopBackgroundProcess('sleep')
spec = { 'default': default }
