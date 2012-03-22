
def fail():
    # raise any exception in the main thread to fail a test case
    raise RuntimeError('SyncDET is so fun')
spec = { 'default': fail }
