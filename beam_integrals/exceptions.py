class BeamTypesException(Exception):
    """A generic exception for all others to extend""" 


class PerformanceWarning(UserWarning):
    """Warning issued when something causes a performance degradation"""


class InvalidBeamTypeError(BeamTypesException):
    """The given value can't be coerced to a valid beam type"""
