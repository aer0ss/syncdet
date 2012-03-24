
from case import startSubprocess

def subprocess():
    startSubprocess(['ls', '-l'])
spec = { 'default': subprocess }
