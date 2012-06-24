from nose.tools import make_decorator
import warnings as warnings_mod


__all__ = ['issues_warnings',]


def issues_warnings(*warnings):
    """
    Test must issue one of expected warnings to pass.
    
    Based on `nose.tools.raises`.
    
    Example use::
    
      @issues_warnings(UserWarning, DeprecationWarning)
      def test_issues_deprecation_warning():
          import warnings
          warnings.warn('This test passes')
    
      @issues_warnings(Warning)
      def test_that_fails_by_passing():
          pass
    """
    valid = ' or '.join([w.__name__ for w in warnings])
    
    def decorate(func):
        name = func.__name__
        
        def newfunc(*arg, **kw):
            with warnings_mod.catch_warnings(record=True) as issued_warnings:
                warnings_mod.simplefilter('always')
                
                func(*arg, **kw)
                
                interesting = [
                    w for w in issued_warnings
                    if issubclass(w.category, warnings)
                ]
                if not interesting:
                    message = "%s() did not issue %s" % (name, valid)
                    raise AssertionError(message)
        
        newfunc = make_decorator(func)(newfunc)
        return newfunc
    
    return decorate


# Based on `nose.tools`
#
# Expose assert* from unittest.TestCase
# - give them pep8 style names
#
import re
import sys


# Python 2.7 introduced new assert* methods in `unittest.TestCase`, fallback to
# backported library if Python < 2.7 
if sys.version_info < (2, 7):
    import unittest2 as unittest #@UnusedImport
else:
    import unittest #@Reimport


caps = re.compile('([A-Z])')

def pep8(name):
    return caps.sub(lambda m: '_' + m.groups()[0].lower(), name)

class Dummy(unittest.TestCase):
    maxDiff = None # Show the entire diff in failure messages
    
    def nop(self):
        pass
_t = Dummy('nop')

for at in [ at for at in dir(_t)
            if at.startswith('assert') and not '_' in at ]:
    pepd = pep8(at)
    vars()[pepd] = getattr(_t, at)
    __all__.append(pepd)

del Dummy
del _t
del pep8
