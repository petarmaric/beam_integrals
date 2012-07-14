class BeamTypesException(Exception):
    """A generic exception for all others to extend""" 


class PerformanceWarning(UserWarning):
    """Warning issued when something causes a performance degradation"""


class InvalidBeamTypeError(BeamTypesException):
    """The given value can't be coerced to a valid beam type"""


class RootfinderError(BeamTypesException):
    """Exception raised when something causes a rootfinder error"""


class UndefinedRootError(RootfinderError):
    """Root is undefined for the given mode"""


class MultipleRootsError(RootfinderError):
    """Multiple roots found while guessing the optimal `mu_m` search interval"""


class BestRootsCacheError(RootfinderError):
    """Exception raised when something causes a best roots cache error"""


class UnableToLoadBestRootsCacheError(BestRootsCacheError):
    """Unable to load the best roots cache"""


class ModeNotFoundInCacheError(BestRootsCacheError):
    """Given mode not found in the best roots cache"""
