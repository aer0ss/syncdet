import os, time

import case
from lib import *

def entry():
    luck = getUniquePath().__hash__() % case.getSysCount()
    if luck == case.getSysId():
        setOnline(False)
        time.sleep(1)
        setOnline(True)

spec = { 'default': entry }