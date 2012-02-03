import case
import lib

def entry():
    lib.killFS()
    return 'killed AeroFS, ignoring errors'

spec = { 'default': entry }
