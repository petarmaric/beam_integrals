from itertools import chain
from math import ceil, floor
from nose.plugins.skip import SkipTest
import shutil
from sympy import Abs
import tempfile
from beam_integrals import a, mu_m
from beam_integrals import characteristic_equation_solvers as ces
from beam_integrals.beam_types import BaseBeamType
from beam_integrals.integrals import BaseIntegral, integrate
import tests
from tests.tools import assert_almost_equal, assert_equal, assert_less_equal, assert_is #@UnresolvedImport


INTEGRAL_CLOSED_FORMS_FOR_SIMPLY_SUPPORTED_BEAM = {
    1:   a/2.,
    2:  (a/2.) * (mu_m/a)**2,
    3: -(a/2.) * (mu_m/a)**2,
    5: -(a/2.) * (mu_m/a)**2,
    7:  (a/2.) * (mu_m/a)**4,
}


def setup():
    global cache_keys_seen, integral_cache, disk_cache_dir, _old_best_roots_cache
    
    cache_keys_seen = set()
    integral_cache = {}
    
    _old_best_roots_cache = ces.best_roots_cache
    disk_cache_dir = tempfile.mkdtemp()
    ces.best_roots_cache = ces.BestRootsCache(disk_cache_dir)
    ces.best_roots_cache.regenerate(tests.MAX_MODE, tests.DECIMAL_PRECISION)

def teardown():
    cache_keys_seen.clear()
    ces.best_roots_cache = _old_best_roots_cache
    shutil.rmtree(disk_cache_dir)

def iterate_over_used_variables(integral, spread=1):
    """
    Iterate over 3 smaller (yet representative) mode ranges to speed up tests
    """
    mid = tests.MAX_MODE/2
    mode_ranges = ( 
        (1, 1 + spread),
        (mid - int(floor(spread/2.)), mid + int(ceil(spread/2.))),
        (tests.MAX_MODE - spread, tests.MAX_MODE)
    )
    return chain.from_iterable(
        integral.iterate_over_used_variables(start_mode=start, max_mode=stop)
        for start, stop in mode_ranges
    )

def test_integrate():
    for integral_id in BaseIntegral.plugins.valid_ids: #@UndefinedVariable
        integral = BaseIntegral.coerce(integral_id) #@UndefinedVariable
        
        # Skip integrals with parents, as they behave the same
        if integral.has_parent():
            continue
        
        integral_cache[integral_id] = {}
        
        for beam_type_id in BaseBeamType.plugins.valid_ids: #@UndefinedVariable
            # Clear out `cache_keys_seen` before testing a new
            # beam_type/integral combination
            cache_keys_seen.clear()
            
            for m, t, v, n in iterate_over_used_variables(integral):
                yield check_integrate, integral_id, beam_type_id, m, t, v, n

def check_integrate(integral_id, beam_type_id, m, t, v, n):
    integral = BaseIntegral.coerce(integral_id) #@UndefinedVariable
    
    cache_key = integral.cache_key(m, t, v, n, max_mode=tests.MAX_MODE)
    if cache_key in cache_keys_seen: # Skip cached integrals
        raise SkipTest
    
    cache_keys_seen.add(cache_key)
    beam_type = BaseBeamType.coerce(beam_type_id) #@UndefinedVariable
    
    result, error = integrate(
        integral, beam_type,
        a=1.,
        m=m, t=t, v=v, n=n,
        decimal_precision=tests.DECIMAL_PRECISION,
        error=True
    )
    
    # CHEAT: Cache the integration results to speed up `test_simply_supported_beam_closed_form`
    if beam_type_id == 1 and integral_id in INTEGRAL_CLOSED_FORMS_FOR_SIMPLY_SUPPORTED_BEAM:
        integral_cache[integral_id][(m, t, v, n)] = result
    
    assert_less_equal(error, tests.MAX_ERROR_TOLERANCE)

def test_integrate_options():
    integral = BaseIntegral.coerce(1) #@UndefinedVariable
    beam_type = BaseBeamType.coerce(1) #@UndefinedVariable
    
    def base_integrate(**kwargs):
        return integrate(
            integral, beam_type,
            a=1.,
            m=1, n=1,
            decimal_precision=tests.DECIMAL_PRECISION,
            **kwargs
        )
    
    # When called with `error=True` `integrate` should return a `(result, error)` tuple
    result_with_error_info = base_integrate(error=True)
    assert_is(type(result_with_error_info), tuple)
    
    # `integrate` should return the same `result` regardless of the `error` flag
    assert_equal(base_integrate(), result_with_error_info[0])

def test_simply_supported_beam_closed_form():
    for integral_id in INTEGRAL_CLOSED_FORMS_FOR_SIMPLY_SUPPORTED_BEAM:
        integral = BaseIntegral.coerce(integral_id) #@UndefinedVariable
        
        # Clear out `cache_keys_seen` before testing a new integral
        cache_keys_seen.clear()
        
        for m, t, v, n in iterate_over_used_variables(integral):
            yield check_simply_supported_beam_closed_form, integral_id, m, t, v, n

def check_simply_supported_beam_closed_form(integral_id, m, t, v, n):
    integral = BaseIntegral.coerce(integral_id) #@UndefinedVariable
    
    cache_key = integral.cache_key(m, t, v, n, max_mode=tests.MAX_MODE)
    if cache_key in cache_keys_seen: # Skip cached integrals
        raise SkipTest
    
    cache_keys_seen.add(cache_key)
    beam_type = BaseBeamType.coerce(1) #@UndefinedVariable
    
    # SPEED HACK: Integration already done in `test_integrate`
    result = integral_cache[integral_id][(m, t, v, n)]
    
    if m != n:
        # The result should be 0, as per D.D. Milasinovic
        assert_less_equal(Abs(result), tests.MAX_ERROR_TOLERANCE)
    else:
        closed_form = INTEGRAL_CLOSED_FORMS_FOR_SIMPLY_SUPPORTED_BEAM[integral_id]
        closed_form_result = closed_form.evalf(n=tests.DECIMAL_PRECISION, subs={
            'a': 1.,
            'mu_m': ces.find_best_root(beam_type, m, tests.DECIMAL_PRECISION)
        })
        assert_almost_equal(result, closed_form_result, delta=tests.MAX_ERROR_TOLERANCE)
