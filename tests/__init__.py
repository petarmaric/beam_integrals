import os
from beam_integrals import DEFAULT_MAX_MODE, DEFAULT_DECIMAL_PRECISION


MAX_MODE = DEFAULT_MAX_MODE
DECIMAL_PRECISION = DEFAULT_DECIMAL_PRECISION

IEEE_754_FLOATING_POINT_PRECISIONS = (16, 32, 64, 80, 128) # Size in bits

MAX_ERROR_TOLERANCE_DECIMALS = 16
MAX_ERROR_TOLERANCE = 10 ** -MAX_ERROR_TOLERANCE_DECIMALS


env = lambda e: os.environ.get(e, '').lower()
if env('IGNORE_SYMPY_MEMORY_LEAK') != 'yes' and env('SYMPY_USE_CACHE') != 'no':
    raise RuntimeError(
        "To avoid a well-known memory leak (see goo.gl/B3PhB and goo.gl/pGj10) "\
        "you're strongly advised to disable SymPy internal caching, by "\
        "setting the environment variable 'SYMPY_USE_CACHE=no' before running "\
        "tests (tests may run a bit slower). To ignore this error set the "\
        "environment variable 'IGNORE_SYMPY_MEMORY_LEAK=yes'."
    )


# When testing on Windows monkey patch `multiprocessing.Pool()` to use a dummy
# implementation, to prevent the entire system from blowing up (quite literally,
# fork bomb). This issue is caused by the lack of a sensible `fork()` syscall on
# Windows and weird issues when combining `nose` with `multiprocessing`. It's a
# well known problem:
#    * http://code.google.com/p/python-nose/issues/detail?id=398
#    * http://bugs.python.org/issue11240
if os.name == 'nt':
    import multiprocessing
    import multiprocessing.dummy
    
    multiprocessing.Pool = multiprocessing.dummy.Pool
