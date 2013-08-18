from nose.tools import eq_
from nose_extra_tools import assert_is #@UnresolvedImport
from sympy import diff
from beam_integrals import y
from beam_integrals.beam_types import BaseBeamType
import tests as t


def setup():
    # Clear the derivative caches before any tests
    for beam_type in BaseBeamType.plugins.instances: #@UndefinedVariable
        beam_type._Y_m_derivatives_cache = None

def test_caching():
    modes = range(1, t.MAX_MODE+1)
    orders = range(1, BaseBeamType._Y_M_DERIVATIVES_CACHE_MAX_ORDER+1)
    for beam_type_id in BaseBeamType.plugins.valid_ids: #@UndefinedVariable
        for mode in modes:
            for order in orders:
                yield check_caching, beam_type_id, mode, order

def check_caching(beam_type_id, mode, order):
    beam_type = BaseBeamType.coerce(beam_type_id) #@UndefinedVariable
    
    # Cached derivative should be equal to a freshly computed derivative
    cached_derivative = beam_type.Y_m_derivative_from_cache(mode, order)
    eq_(cached_derivative, diff(beam_type.Y_m(mode), y, order))
    
    # Continuous cache hits should return same objects
    cache_hit = beam_type.Y_m_derivative_from_cache(mode, order)
    assert_is(cache_hit, cached_derivative)
