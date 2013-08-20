from friendly_name_mixin import FriendlyNameFromClassMixin
from simple_plugins import PluginMount
from sympy import cos, cosh, diff, Float, pi, sin, sinh, tan, tanh
from . import a, y, mu_m


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
   
    def Y_m(self, mode):
        raise NotImplementedError
    
    _Y_M_DERIVATIVES_CACHE_MAX_ORDER = 2
    _Y_m_derivatives_cache = None
    def Y_m_derivative_from_cache(self, mode, order):
        if self._Y_m_derivatives_cache is None:
            self._Y_m_derivatives_cache = {}
            cache_keys = [None] + list(self.dont_improve_mu_m_for_modes)
            for n in range(1, self._Y_M_DERIVATIVES_CACHE_MAX_ORDER+1):
                self._Y_m_derivatives_cache[n] = dict(
                    (k, diff(self.Y_m(k), y, n)) 
                    for k in cache_keys
                )
        
        key = mode if mode in self.dont_improve_mu_m_for_modes else None
        return self._Y_m_derivatives_cache[order][key]


class SimplySupportedBeam(BaseBeamType):
    id = 1 #@ReservedAssignment
    characteristic_function = sin(mu_m)
    
    def mu_m_initial_guess(self, mode):
        return mode * pi
   
    def Y_m(self, mode): #@UnusedVariable
        return sin(mu_m*y/a)


class ClampedClampedBeam(BaseBeamType):
    id = 2 #@ReservedAssignment
    characteristic_function = cos(mu_m)*cosh(mu_m) - 1
    
    def mu_m_initial_guess(self, mode):
        return (2*mode + 1) * pi/2
   
    def Y_m(self, mode): #@UnusedVariable
        return 1/(cos(mu_m)-cosh(mu_m)) * (
              sin (mu_m*y/a)*cos (mu_m) - sin (mu_m*y/a)*cosh(mu_m)
            - sinh(mu_m*y/a)*cos (mu_m) + sinh(mu_m*y/a)*cosh(mu_m)
            - cos (mu_m*y/a)*sin (mu_m) + cosh(mu_m*y/a)*sin (mu_m)
            + cos (mu_m*y/a)*sinh(mu_m) - cosh(mu_m*y/a)*sinh(mu_m)
        )


class ClampedFreeBeam(BaseBeamType):
    id = 3 #@ReservedAssignment
    characteristic_function = cos(mu_m)*cosh(mu_m) + 1
    
    def mu_m_initial_guess(self, mode):
        return (2*mode - 1) * pi/2
   
    def Y_m(self, mode): #@UnusedVariable
        return 1/(cos(mu_m)+cosh(mu_m)) * (
              sin (mu_m*y/a)*cos (mu_m) + sin (mu_m*y/a)*cosh(mu_m)
            - sinh(mu_m*y/a)*cos (mu_m) - sinh(mu_m*y/a)*cosh(mu_m)
            - cos (mu_m*y/a)*sin (mu_m) + cosh(mu_m*y/a)*sin (mu_m)
            - cos (mu_m*y/a)*sinh(mu_m) + cosh(mu_m*y/a)*sinh(mu_m)
        )


class ClampedSimplySupportedBeam(BaseBeamType):
    id = 4 #@ReservedAssignment
    characteristic_function = tan(mu_m) - tanh(mu_m)
    
    def mu_m_initial_guess(self, mode):
        return (4*mode + 1) * pi/4
   
    def Y_m(self, mode): #@UnusedVariable
        return 1/sinh(mu_m) * (sin(mu_m*y/a)*sinh(mu_m) - sinh(mu_m*y/a)*sin(mu_m))


class SimplySupportedFreeBeam(ClampedSimplySupportedBeam):
    id = 5 #@ReservedAssignment
    
    dont_improve_mu_m_for_modes = (1,)
    
    def mu_m_initial_guess(self, mode):
        # Special case for this mode
        if mode == 1:
            return Float(1)
        
        return super(SimplySupportedFreeBeam, self).mu_m_initial_guess(mode-1)
   
    def Y_m(self, mode):
        # Special case for this mode
        if mode == 1:
            return y/a
        
        return 1/sinh(mu_m) * (sin(mu_m*y/a)*sinh(mu_m) + sinh(mu_m*y/a)*sin(mu_m))


class FreeFreeBeam(ClampedClampedBeam):
    id = 6 #@ReservedAssignment
    
    dont_improve_mu_m_for_modes = (1, 2)
    
    def mu_m_initial_guess(self, mode):
        # Special case for these modes
        if mode == 1:
            return Float(0)
        elif mode == 2:
            return Float(1)
        
        return super(FreeFreeBeam, self).mu_m_initial_guess(mode-2)
   
    def Y_m(self, mode):
        # Special case for these modes
        if mode == 1:
            return Float(1)
        elif mode == 2:
            return 1 - 2*y/a
        
        return 1/(cos(mu_m)+cosh(mu_m)) * (
              sin (mu_m*y/a)*cos (mu_m) + sin (mu_m*y/a)*cosh(mu_m)
            - sinh(mu_m*y/a)*cos (mu_m) - sinh(mu_m*y/a)*cosh(mu_m)
            - cos (mu_m*y/a)*sin (mu_m) + cosh(mu_m*y/a)*sin (mu_m)
            - cos (mu_m*y/a)*sinh(mu_m) + cosh(mu_m*y/a)*sinh(mu_m)
        )
