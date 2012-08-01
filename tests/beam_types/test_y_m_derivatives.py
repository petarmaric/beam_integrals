from nose.tools import eq_
from sympy import diff
from beam_integrals import y
from beam_integrals import beam_types as bt
import tests as t
from tests.tools import assert_is #@UnresolvedImport


def setup():
    # Clear the derivative caches before any tests
    for beam_type in bt.ALL_BEAM_TYPE_INSTANCES:
        beam_type._Y_m_derivatives_cache = None

def test_caching():
    modes = range(1, t.MAX_MODE+1)
    orders = range(1, bt.BaseBeamType._Y_M_DERIVATIVES_CACHE_MAX_ORDER+1)
    for beam_type_id in bt.VALID_BEAM_TYPE_IDS:
        for mode in modes:
            for order in orders:
                yield check_caching, beam_type_id, mode, order

def check_caching(beam_type_id, mode, order):
    beam_type = bt.coerce_beam_type(beam_type_id)
    
    # Cached derivative should be equal to a freshly computed derivative
    cached_derivative = beam_type.Y_m_derivative_from_cache(mode, order)
    eq_(cached_derivative, diff(beam_type.Y_m(mode), y, order))
    
    # Continuous cache hits should return same objects
    cache_hit = beam_type.Y_m_derivative_from_cache(mode, order)
    assert_is(cache_hit, cached_derivative)
