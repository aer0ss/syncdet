"""
This test case demonstrates how to use sync primitives.
"""

from syncdet.case import sync

def default():
    sync.sync_prev(0)
    print 'the test machines should print this line one by one'
    sync.sync_next(0)

    sync.sync(0)
    print 'the test machines should print this line in parallel'

spec = {
        'default': default,
        }
