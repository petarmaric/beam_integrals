import multiprocessing
from operator import itemgetter
import os
import cPickle as pickle
from friendly_name_mixin import FriendlyNameFromClassMixin
from simple_plugins import AttrDict, PluginMount
from sympy import Abs, Float, nan, mpmath, sign
from . import PROJECT_SETTINGS_DIR, DEFAULT_MAX_MODE, DEFAULT_DECIMAL_PRECISION
from . import exceptions as exc
from .beam_types import BaseBeamType


class BaseRootfinder(FriendlyNameFromClassMixin):
    max_iterations = 100
    
    __metaclass__ = PluginMount
    
    class Meta:
        id_field = 'solver_name'
        id_field_coerce = str
    
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
                    verify=False,
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
            raise exc.UndefinedRootError(
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
                raise exc.MultipleRootsError(
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


def find_root_candidates(beam_type, mode, decimal_precision=DEFAULT_DECIMAL_PRECISION, **kwargs):
    return dict(
        (name, rootfinder(beam_type, mode, decimal_precision, **kwargs))
        for name, rootfinder in BaseRootfinder.plugins.id_to_instance.items()
    )

def find_best_root(beam_type, mode, decimal_precision=DEFAULT_DECIMAL_PRECISION,
    include_error=False, use_cache=True, cache_instance=None, **kwargs):
    if use_cache:
        cache_instance = cache_instance or best_roots_cache
        result = cache_instance.get(beam_type, mode, decimal_precision)
    else:
        result = min(
            find_root_candidates(beam_type, mode, decimal_precision, **kwargs).values(),
            key=itemgetter(1)
        )
    
    return result if include_error else result[0]

def _init_pool(*data): #pragma: no cover
    global _pool_data
    
    data_keys = 'beam_type, decimal_precision, include_error, kwargs'.split(', ')
    _pool_data = AttrDict(zip(data_keys, data))

def _worker(mode): #pragma: no cover
    c = _pool_data
    return find_best_root(
        c.beam_type, mode, c.decimal_precision, include_error=c.include_error,
        use_cache=False, **c.kwargs
    )

def find_best_roots(beam_type, max_mode=DEFAULT_MAX_MODE,
    decimal_precision=DEFAULT_DECIMAL_PRECISION, include_error=True, **kwargs):
    pool = multiprocessing.Pool(
        initializer=_init_pool,
        initargs=(beam_type, decimal_precision, include_error, kwargs)
    )
    results = pool.map(func=_worker, iterable=range(1, max_mode+1))
    
    pool.close()
    pool.join()
    return results


class BestRootsCache(object):
    disk_cache_dir = os.path.join(PROJECT_SETTINGS_DIR, 'cache', 'characteristic-equations')
    _ram_cache = {}
    
    def __init__(self, disk_cache_dir=None):
        self.disk_cache_dir = disk_cache_dir or self.disk_cache_dir
        if not os.path.exists(self.disk_cache_dir):
            os.makedirs(self.disk_cache_dir)
    
    def disk_cache_filename(self, decimal_precision=DEFAULT_DECIMAL_PRECISION):
        return os.path.join(
            self.disk_cache_dir,
            "best-roots.decimal-precision=%d.pickle" % decimal_precision
        )
    
    def regenerate(self, max_mode=DEFAULT_MAX_MODE, decimal_precision=DEFAULT_DECIMAL_PRECISION, **kwargs):
        results = dict(
            (beam_type.id, find_best_roots(beam_type, max_mode, decimal_precision, **kwargs))
            for beam_type in BaseBeamType.plugins.instances #@UndefinedVariable
        )
        
        with open(self.disk_cache_filename(decimal_precision), 'wb') as f:
            pickle.dump(results, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        if decimal_precision in self._ram_cache: # Clear out the old RAM cache
            del self._ram_cache[decimal_precision]
    
    def _load_disk_cache(self, decimal_precision=DEFAULT_DECIMAL_PRECISION):
        filename = self.disk_cache_filename(decimal_precision)
        try:
            with open(filename, 'rb') as f:
                self._ram_cache[decimal_precision] = pickle.load(f)
        except (IOError, pickle.UnpicklingError), e:
            raise exc.UnableToLoadBestRootsCacheError(
                "Unable to load cache from '%s': %s. You'll need to "\
                "regenerate the cache by calling the console app "\
                "'beam_integrals best-roots-of-characteristic-equations-regenerate-cache' "\
                "or by using "\
                "'beam_integrals.characteristic_equation_solvers.best_roots_cache.regenerate' "\
                "Python API call." %
                (filename, e)
            )
    
    def get(self, beam_type, mode, decimal_precision=DEFAULT_DECIMAL_PRECISION):
        if decimal_precision not in self._ram_cache:
            self._load_disk_cache(decimal_precision)
        
        try:
            if mode <= 0:
                raise exc.InvalidModeError("Mode has to be a positive number (%s given)" % mode)
            
            # Mode list is 0 indexed
            return self._ram_cache[decimal_precision][beam_type.id][mode-1]
        except KeyError:
            # Old version cache, doesn't support this beam type
            raise exc.BeamTypeNotFoundInCacheError(
                "No best root found in cache for %s. You'll "\
                "need to regenerate the cache by calling the console app "\
                "'beam_integrals best-roots-of-characteristic-equations-regenerate-cache' "\
                "or by using "\
                "'beam_integrals.characteristic_equation_solvers.best_roots_cache.regenerate' "\
                "Python API call." % beam_type
            )
        except IndexError:
            raise exc.ModeNotFoundInCacheError(
                "No best root found in cache for %s when mode = %d. You'll "\
                "need to regenerate the cache by calling the console app "\
                "'beam_integrals best-roots-of-characteristic-equations-regenerate-cache' "\
                "or by using "\
                "'beam_integrals.characteristic_equation_solvers.best_roots_cache.regenerate' "\
                "Python API call. Please remember to increase max_mode to the "\
                "desired limit." %
                (beam_type, mode)
            )


best_roots_cache = BestRootsCache()
