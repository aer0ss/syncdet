
from case import startSubprocess

def spawn_subprocess():
    startSubprocess(['echo', 'hello from a subprocess'])
spec = { 'default': spawn_subprocess }
