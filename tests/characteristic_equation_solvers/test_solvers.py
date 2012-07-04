from nose.tools import raises
from nose.plugins.skip import SkipTest
from sympy.mpmath.libmp.libmpf import prec_to_dps
from beam_integrals import beam_types as bt
from beam_integrals.characteristic_equation_solvers import find_best_root
import tests as t
from tests.tools import assert_less_equal #@UnresolvedImport


def test_find_best_root():
    modes = range(1, t.MAX_MODE+1)
    for beam_type_id in bt.VALID_BEAM_TYPE_IDS:
        for mode in modes:
            yield check_find_best_root, beam_type_id, mode

def check_find_best_root(beam_type_id, mode):
    beam_type = bt.coerce_beam_type(beam_type_id)
    
    _, mu_m_error = find_best_root(
        beam_type,
        mode,
        t.DECIMAL_PRECISION,
        include_error=True,
    )
    
    # Special case for this mode, don't check the `mu_m_error`
    if mode in beam_type.dont_improve_mu_m_for_modes:
        raise SkipTest
    
    assert_less_equal(mu_m_error, t.MAX_ERROR_TOLERANCE)

def test_fail_for_ieee_754_floating_point_precision():
    for binary_precision in t.IEEE_754_FLOATING_POINT_PRECISIONS:
        yield check_fail_for_ieee_754_floating_point_precision, binary_precision

@raises(AssertionError, ValueError)
def check_fail_for_ieee_754_floating_point_precision(binary_precision):
    decimal_precision = prec_to_dps(binary_precision)
    modes = range(t.MAX_MODE, 0, -1) # Higher modes cause the precision error
    for mode in modes:
        for beam_type in bt.ALL_BEAM_TYPE_INSTANCES:
            _, mu_m_error = find_best_root(
                beam_type,
                mode,
                decimal_precision,
                include_error=True,
            )
            
            # Special case for this mode, don't check the `mu_m_error`
            if mode in beam_type.dont_improve_mu_m_for_modes:
                continue
            
            assert_less_equal(mu_m_error, t.MAX_ERROR_TOLERANCE)