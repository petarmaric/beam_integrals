from warnings import warn
from .exceptions import InvalidBeamTypeError, PerformanceWarning
from .utils import FriendlyNameFromClassMixin, PluginMount


class BaseBeamType(FriendlyNameFromClassMixin):
    id = None #@ReservedAssignment
    
    __metaclass__ = PluginMount
    
    def __str__(self):
        return "%s (id=%d)" % (self.name, self.id)
    
    @property
    def filename(self):
        return "%d-%s" % (self.id, '-'.join(self.name.lower().split()))


class SimplySupportedBeam(BaseBeamType):
    id = 1 #@ReservedAssignment


class ClampedClampedBeam(BaseBeamType):
    id = 2 #@ReservedAssignment


class ClampedFreeBeam(BaseBeamType):
    id = 3 #@ReservedAssignment


class ClampedSimplySupportedBeam(BaseBeamType):
    id = 4 #@ReservedAssignment


class SimplySupportedFreeBeam(ClampedSimplySupportedBeam):
    id = 5 #@ReservedAssignment


class FreeFreeBeam(ClampedClampedBeam):
    id = 6 #@ReservedAssignment


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
