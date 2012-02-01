import case
import lib

def entry():
    lib.terminateFS(True)
    return 'terminated AeroFS, ignoring errors'

spec = { 'default': entry }
