import os
from sympy import mpmath, symbols


if 'MPMATH_NOGMPY' not in os.environ and mpmath.libmp.BACKEND == 'python': #@UndefinedVariable, pragma: no cover
    import warnings
    from simple_plugins import PerformanceWarning

    warnings.warn(
        'gmpy is not available for speedups (code will still run correctly, '\
        'but much slower at high precision)',
        category=PerformanceWarning
    )


PROJECT_SETTINGS_DIR = os.path.expanduser('~/.beam_integrals')
DEFAULT_MAX_MODE = 100
DEFAULT_DECIMAL_PRECISION = 155

__version__ = '1.1.1'


# Commonly used symbols
a, y, mu_m = symbols('a, y, mu_m')
