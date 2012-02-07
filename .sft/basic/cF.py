import os, time

import case
from lib import *

str = 'written by sys 0'

def put():
    print 'put', getUniquePath()
    file = open(getUniquePath(), 'wb')
    file.write(str)

def get():
    print 'get', getUniquePath()
    waitFile(getUniquePath(), str)


spec = { 'entries': [put], 'default': get }