"""
This module provides methods to assert correct behaviour of a test.

The methods are similar in signature to JUnit's Assert methods
and Python's unittest.TestCase methods. If needed, extend this API
with those methods in unittest.TestCase.
"""

class _Failure(Exception): pass

def fail(msg = ''):
    raise _Failure(msg)

def assertTrue(cond, msg = 'condition must be true'):
    if not cond: raise _Failure(msg)

def assertFalse(cond, msg = 'condition must be false'):
    assertTrue(not cond, msg)

def assertEqual(expected, actual):
    assertTrue(expected == actual,
               ('"{0}" and "{1}" were expected to be equal, but are not'
               ).format(str(expected), str(actual)))

def assertNotEqual(first, second):
    assertFalse(first == second,
               ('"{0}" and "{1}" were expected to be not equal, but are'
               ).format(str(first), str(second)))
