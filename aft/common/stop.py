import case
import lib

def entry():
    lib.terminateFS()
    return 'terminated AeroFS'

spec = { 'default': entry }
