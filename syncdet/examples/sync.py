import case

def sync():
    case.syncPrev(0)
    print 'the test machines should print this line one by one'
    case.syncNext(0)

    case.sync(0)
    print 'the test machines should print this line in parallel'

spec = {
        'default': sync,
        }
