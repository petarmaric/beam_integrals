from sympy import cos, cosh, Float, pi, sin, tan, tanh
from warnings import warn
from . import mu_m
from .exceptions import InvalidBeamTypeError, PerformanceWarning
from .utils import FriendlyNameFromClassMixin, PluginMount


class BaseBeamType(FriendlyNameFromClassMixin):
    id = None #@ReservedAssignment
    characteristic_function = None
    
    dont_improve_mu_m_for_modes = ()
    mu_m_initial_search_width = pi/10
    mu_m_increase_search_width_by = Float(1.05)
    
    __metaclass__ = PluginMount
    
    def __str__(self):
        return "%s (id=%d)" % (self.name, self.id)
    
    @property
    def filename(self):
        return "%d-%s" % (self.id, '-'.join(self.name.lower().split()))
    
    @property
    def characteristic_equation_str(self):
        return "%s = 0" % self.characteristic_function
    
    def mu_m_initial_guess(self, mode):
        raise NotImplementedError


class SimplySupportedBeam(BaseBeamType):
    id = 1 #@ReservedAssignment
    characteristic_function = sin(mu_m)
    
    def mu_m_initial_guess(self, mode):
        return mode * pi


class ClampedClampedBeam(BaseBeamType):
    id = 2 #@ReservedAssignment
    characteristic_function = cos(mu_m)*cosh(mu_m) - 1
    
    def mu_m_initial_guess(self, mode):
        return (2*mode + 1) * pi/2


class ClampedFreeBeam(BaseBeamType):
    id = 3 #@ReservedAssignment
    characteristic_function = cos(mu_m)*cosh(mu_m) + 1
    
    def mu_m_initial_guess(self, mode):
        return (2*mode - 1) * pi/2


class ClampedSimplySupportedBeam(BaseBeamType):
    id = 4 #@ReservedAssignment
    characteristic_function = tan(mu_m) - tanh(mu_m)
    
    def mu_m_initial_guess(self, mode):
        return (4*mode + 1) * pi/4


class SimplySupportedFreeBeam(ClampedSimplySupportedBeam):
    id = 5 #@ReservedAssignment
    
    dont_improve_mu_m_for_modes = (1,)
    
    def mu_m_initial_guess(self, mode):
        # Special case for this mode
        if mode == 1:
            return Float(1)
        
        return super(SimplySupportedFreeBeam, self).mu_m_initial_guess(mode-1)


class FreeFreeBeam(ClampedClampedBeam):
    id = 6 #@ReservedAssignment
    
    dont_improve_mu_m_for_modes = (1, 2)
    
    def mu_m_initial_guess(self, mode):
        # Special case for this mode
        if mode == 1:
            return Float(0)
        elif mode == 2:
            return Float(1)
        
        return super(FreeFreeBeam, self).mu_m_initial_guess(mode-2)


ID_TO_BEAM_TYPE_CLASS = dict((cls.id, cls) for cls in BaseBeamType.plugins)
ALL_BEAM_TYPES_CLASSES = ID_TO_BEAM_TYPE_CLASS.values()
 
ID_TO_BEAM_TYPE_INSTANCE = dict((k, v()) for k, v in ID_TO_BEAM_TYPE_CLASS.items())
ALL_BEAM_TYPE_INSTANCES = ID_TO_BEAM_TYPE_INSTANCE.values() 

VALID_BEAM_TYPE_IDS = ID_TO_BEAM_TYPE_CLASS.keys()


def coerce_beam_type(beam_type):
    """Coerce the passed value into a right `BaseBeamType` instance"""
    # Check if the passed value is already a `BaseBeamType` instance
    if isinstance(beam_type, BaseBeamType):
        warn(
            'Creating too many BaseBeamType instances may be expensive, '\
            'passing a beam type id is generally preferred',
            category=PerformanceWarning
        )
        return beam_type # No coercion needed
    
    # Check if the passed value is a `BaseBeamType` subclass
    try:
        if issubclass(beam_type, BaseBeamType):
            warn(
                'Creating too many BaseBeamType instances may be expensive, '\
                'passing a beam type id is generally preferred',
                category=PerformanceWarning
            )
            return beam_type()
    except TypeError:
        pass # Passed value is not a class
    
    # Check if the passed value is a valid beam type id
    try:
        beam_type_id = int(beam_type)
        
        try:
            return ID_TO_BEAM_TYPE_INSTANCE[beam_type_id]
        except KeyError:
            raise InvalidBeamTypeError("%d is not a valid beam type id" % beam_type_id)
    except (TypeError, ValueError):
        pass # Passed value can't be converted to an integer, not a beam type id
    
    # Can't coerce an unknown type
    raise InvalidBeamTypeError("Can't coerce %r to a valid beam type" % beam_type)
