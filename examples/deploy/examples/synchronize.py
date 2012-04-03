'''This test case demonstrates how to use sync primitives.'''

from syncdet.case import sync

def default():
    sync.syncPrev(0)
    print 'the test machines should print this line one by one'
    sync.syncNext(0)

    sync.sync(0)
    print 'the test machines should print this line in parallel'

spec = {
        'default': default,
        }
