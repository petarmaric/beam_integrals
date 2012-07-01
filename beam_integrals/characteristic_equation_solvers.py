from operator import itemgetter
from sympy import Abs, Float, nan, mpmath, sign
from . import DEFAULT_DECIMAL_PRECISION
from .exceptions import MultipleRootsError, UndefinedRootError
from .utils import FriendlyNameFromClassMixin, PluginMount


class BaseRootfinder(FriendlyNameFromClassMixin):
    max_iterations = 10**9
    
    __metaclass__ = PluginMount
    
    @property
    def solver_name(self):
        return self.name.lower().split()[0]
    
    def _get_f(self, beam_type, decimal_precision):
        def f(mu_m):
            return beam_type.characteristic_function.evalf(
                n=decimal_precision,
                subs={'mu_m': mu_m}
            )
        
        return f
    
    def find_root(self, beam_type, mode, decimal_precision=DEFAULT_DECIMAL_PRECISION, **kwargs):
        if mode in beam_type.dont_improve_mu_m_for_modes:
            mu_m = beam_type.mu_m_initial_guess(mode).evalf(n=decimal_precision)
            mu_m_error = nan # characteristic equation is not defined for this `mode`
        else:
            mu_m = self.improve_mu_m(beam_type, mode, decimal_precision, **kwargs)
            f = self._get_f(beam_type, decimal_precision)
            mu_m_error = Abs(f(mu_m))
        
        return mu_m, mu_m_error
    
    def improve_mu_m(self, beam_type, mode, decimal_precision=DEFAULT_DECIMAL_PRECISION, **kwargs):
        f = self._get_f(beam_type, decimal_precision)
        
        with mpmath.workdps(decimal_precision):
            # If not converted to `sympy.Float` precision will be lost after the
            # original `mpmath` context is restored
            return Float(
                mpmath.findroot(
                    f=f,
                    x0=self.x0(beam_type, mode, decimal_precision),
                    solver=self.solver_name,
                    maxsteps=self.max_iterations,
                    **kwargs
                ),
                decimal_precision
            )
    
    def x0(self, beam_type, mode, decimal_precision=DEFAULT_DECIMAL_PRECISION):
        raise NotImplementedError
    
    def __call__(self, beam_type, mode, decimal_precision=DEFAULT_DECIMAL_PRECISION, **kwargs):
        return self.find_root(beam_type, mode, decimal_precision, **kwargs)


class BaseIntervalBasedRootfinder(BaseRootfinder):
    def x0(self, beam_type, mode, decimal_precision=DEFAULT_DECIMAL_PRECISION):
        """Guesses the optimal `mu_m` search interval"""
        if mode in beam_type.dont_improve_mu_m_for_modes:
            raise UndefinedRootError(
                "%s: root is undefined for mode = %d" % (
                    beam_type, mode
            ))
        
        f = self._get_f(beam_type, decimal_precision)
        center = beam_type.mu_m_initial_guess(mode).evalf(n=decimal_precision)
        search_width = beam_type.mu_m_initial_search_width
        
        while True:
            a = (center - search_width/2.).evalf(n=decimal_precision)
            b = (center + search_width/2.).evalf(n=decimal_precision)
            f_a = f(a)
            f_b = f(b)
            
            if f_a == f_b == 0.:
                raise MultipleRootsError(
                    "%s: Found multiple roots in area [%s, %s] for mode = %d" % (
                        beam_type, a, b, mode
                ))
            
            if sign(f_a) == -sign(f_b):
                break
            
            search_width *= beam_type.mu_m_increase_search_width_by
        
        return a, b


class BaseStartingPointBasedRootfinder(BaseRootfinder):
    def x0(self, beam_type, mode, decimal_precision=DEFAULT_DECIMAL_PRECISION):
        return beam_type.mu_m_initial_guess(mode).evalf(n=decimal_precision)


class AndersonRootfinder(BaseIntervalBasedRootfinder):
    pass


# Disabled, as it's too slow and not a top rootfinder
#class BisectRootfinder(BaseIntervalBasedRootfinder):
#    pass


class IllinoisRootfinder(BaseIntervalBasedRootfinder):
    pass


class PegasusRootfinder(BaseIntervalBasedRootfinder):
    pass


# Disabled, as it's too slow and not a top rootfinder
#class RidderRootfinder(BaseIntervalBasedRootfinder):
#    pass


class SecantRootfinder(BaseStartingPointBasedRootfinder):
    pass


ALL_ROOTFINDER_INSTANCES = [cls() for cls in BaseRootfinder.plugins]


def find_root_candidates(beam_type, mode, decimal_precision=DEFAULT_DECIMAL_PRECISION, **kwargs):
    return dict(
        (rootfinder.name, rootfinder(beam_type, mode, decimal_precision, **kwargs))
        for rootfinder in ALL_ROOTFINDER_INSTANCES
    )

def find_best_root(beam_type, mode, decimal_precision=DEFAULT_DECIMAL_PRECISION, include_error=False, **kwargs):
    result = min(
        find_root_candidates(beam_type, mode, decimal_precision, **kwargs).values(),
        key=itemgetter(1)
    )
    return result if include_error else result[0]
