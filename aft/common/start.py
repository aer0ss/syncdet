import os

import lib

def entry():
    lib.launchFS()
    return 'launched AeroFS'
    
spec = { 'default': entry }
