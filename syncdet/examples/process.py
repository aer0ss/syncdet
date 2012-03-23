
from case import startSubprocess

def subprocess():
    startSubprocess('echo', ['ls', '-l'])
spec = { 'default': subprocess }
