import itertools
import re
from friendly_name_mixin import FriendlyNameFromClassMixin
from simple_plugins import PluginMount
from sympy import Float, factor, mpmath, Symbol
from . import a, DEFAULT_DECIMAL_PRECISION
from .characteristic_equation_solvers import find_best_root
from .exceptions import UnableToGuessScaleFunctionError


class BaseIntegral(FriendlyNameFromClassMixin):
    _id_re = re.compile('I(\d+)')
    
    used_variables = ('m', 't', 'v', 'n')
    
    __metaclass__ = PluginMount
    
    def __str__(self):
        return self.name
    
    @property
    def id(self):
        if not hasattr(self, '_id'):
            self._id = int(self._id_re.match(self.name).group(1))
        
        return self._id
    
    @staticmethod
    def _contribute_to_plugins(_plugins):
        _plugins.child_id_to_parent_id = dict(
            (id, _plugins.class_to_id[cls.__base__])
            for cls, id in _plugins.class_to_id.items() #@ReservedAssignment
            if cls.__base__ in _plugins.classes
        )
    
    @classmethod
    def parent_id(cls):
        return cls.plugins.child_id_to_parent_id.get(cls.plugins.class_to_id[cls]) 
    
    @classmethod
    def has_parent(cls):
        return cls.parent_id() is not None
    
    def iterate_over_used_variables(self, max_mode, start_mode=1):
        modes = range(start_mode, max_mode+1)
        get_modes = lambda var: modes if var in self.used_variables else (None,)
        
        var_modes = (get_modes(var) for var in BaseIntegral.used_variables)
        return itertools.product(*var_modes)
    
    def cache_key(self, m, t, v, n, max_mode):
        d = locals()
        return sum(
            d[var] * max_mode**idx
            for idx, var in enumerate(self.used_variables)
        )
    
    def integrand(self, beam_type, m, t, v, n, decimal_precision=DEFAULT_DECIMAL_PRECISION):
        def resolve_mu_m(func, *args, **kwargs):
            def wrapper(mode):
                return func(mode, *args, **kwargs).subs('mu_m',
                    find_best_root(beam_type, mode, decimal_precision)
                )
            
            return wrapper
        
        Y_m = resolve_mu_m(beam_type.Y_m)
        dY_m = resolve_mu_m(beam_type.Y_m_derivative_from_cache, order=1)
        ddY_m = resolve_mu_m(beam_type.Y_m_derivative_from_cache, order=2)
        
        return self._integrand(Y_m, dY_m, ddY_m, m, t, v, n)
    
    def _integrand(self, Y_m, dY_m, ddY_m, m, t, v, n):
        raise NotImplementedError
    
    def guess_scale_function(self, beam_type, m, t, v, n):
        # Special case for these modes due to the mode-specific boundary condition
        if set([m, t, v, n]) & set(beam_type.dont_improve_mu_m_for_modes):
            raise UnableToGuessScaleFunctionError
        
        Y_m = beam_type.Y_m
        dY_m = lambda mode: beam_type.Y_m_derivative_from_cache(mode, order=1)
        ddY_m = lambda mode: beam_type.Y_m_derivative_from_cache(mode, order=2)
        
        integrand = self._integrand(Y_m, dY_m, ddY_m, m, t, v, n)
        factorized = factor(integrand)
        
        scale_by = Float(1) # If nothing is found
        for arg in factorized.args:
            atoms = arg.atoms(Symbol)
            if atoms == set([a]): # Skip atoms with anything besides 'a'
                scale_by = arg
        
        return scale_by*a
    
    def guess_scale_factor(self, beam_type, m, t, v, n):
        return self.guess_scale_function(beam_type, m, t, v, n).as_powers_dict()[a]
    
    def __call__(self, beam_type, m, t, v, n, decimal_precision=DEFAULT_DECIMAL_PRECISION):
        return self.integrand(beam_type, m, t, v, n, decimal_precision)


class BaseIntegralWithSymetricVariables(BaseIntegral):
    def cache_key(self, m, t, v, n, max_mode):
        d = locals()
        values = sorted(d[var] for var in self.used_variables)
        return sum(
            val * max_mode**idx
            for idx, val in enumerate(values)
        )


class I1(BaseIntegralWithSymetricVariables):
    used_variables = ('m', 'n')
    
    def _integrand(self, Y_m, dY_m, ddY_m, m, t, v, n): #@UnusedVariable
        return Y_m(m) * Y_m(n)

class I21(I1): pass


class I2(BaseIntegralWithSymetricVariables):
    used_variables = ('m', 'n')
    
    def _integrand(self, Y_m, dY_m, ddY_m, m, t, v, n): #@UnusedVariable
        return dY_m(m) * dY_m(n)

class I4(I2): pass
class I6(I2): pass
class I8(I2): pass
class I25(I2): pass


class I3(BaseIntegral):
    used_variables = ('m', 'n')
    
    def _integrand(self, Y_m, dY_m, ddY_m, m, t, v, n): #@UnusedVariable
        return ddY_m(m) * Y_m(n)

class I22(I3): pass


class I5(BaseIntegral):
    used_variables = ('m', 'n')
    
    def _integrand(self, Y_m, dY_m, ddY_m, m, t, v, n): #@UnusedVariable
        return Y_m(m) * ddY_m(n)

class I23(I5): pass


class I7(BaseIntegralWithSymetricVariables):
    used_variables = ('m', 'n')
    
    def _integrand(self, Y_m, dY_m, ddY_m, m, t, v, n): #@UnusedVariable
        return ddY_m(m) * ddY_m(n)

class I24(I7): pass


def integrate(integral, beam_type, a, m=None, t=None, v=None, n=None, decimal_precision=DEFAULT_DECIMAL_PRECISION, **kwargs):
    cached_subs = integral(beam_type, m, t, v, n, decimal_precision).subs('a', a)
    f = lambda y: cached_subs.evalf(n=decimal_precision, subs={'y': y})
    
    with mpmath.workdps(decimal_precision):
        result = mpmath.quad(f, (0., a), **kwargs)
        
        # If not converted to `sympy.Float` precision will be lost after the
        # original `mpmath` context is restored
        if isinstance(result, tuple): # Integration error included
            return tuple(Float(x, decimal_precision) for x in result)
        else:
            return Float(result, decimal_precision)
