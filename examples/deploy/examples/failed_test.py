"""
This test case demonstrates how to fail a test.
"""

def fail():
    # raise any exception in the main thread to fail the test
    raise RuntimeError('This test demoes a failed test. Failure is expected here.')
spec = { 'default': fail }
