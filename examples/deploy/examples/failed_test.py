"""
This test case demonstrates how to fail a test.
"""

def fail():
    # raise any exception in the main thread to fail the test
    raise RuntimeError('SyncDET is so fun')
spec = { 'default': fail }
