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

# Using the decorator is not recommended since it can only decorate the entire
# test function, instead of specifying which exact function under test is
# expected to raise.
#
#def expect(ex):
#    """
#    A decorator that expects a particular exception type raised from the
#    decorated function, otherwise fails the test. Usage:
#
#        @except(ExFoo)
#        def function(arg1, arg2):
#            ...
#    """
#    def wrap(func):
#        def wrapper(*args, **kwargs):
#            try:
#                func(*args, **kwargs)
#            except ex:
#                pass
#            else:
#                fail("exception " + ex.__name__ + " is expected")
#        return wrapper
#    return wrap

def expect_exception(func, ex):
    """
    A function wrapper that expects a particular exception type raised from the
    decorated function, otherwise fails the test. Usage:

        def foo(arg1, arg2):
            ...

        expect_exception(foo, ExFoo)(arg1, arg2)

    @param ex the excetion type the caller expect
    """
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except ex:
            pass
        else:
            fail("exception " + ex.__name__ + " is expected")
    return wrapper

