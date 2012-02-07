import os, time, os.path

import case
from lib import *

def put():
    print 'put', getUniquePath()
    os.mkdir(getUniquePath())

def get():
    print 'get', getUniquePath()
    waitDir(getUniquePath())

spec = { 'entries': [put], 'default': get }