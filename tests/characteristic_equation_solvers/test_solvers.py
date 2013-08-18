from nose.tools import raises
from nose.plugins.skip import SkipTest
from nose_extra_tools import assert_less_equal #@UnresolvedImport
from sympy.mpmath.libmp.libmpf import prec_to_dps
from beam_integrals.beam_types import BaseBeamType
from beam_integrals.characteristic_equation_solvers import find_best_root
import tests as t


def test_find_best_root():
    modes = range(1, t.MAX_MODE+1)
    for beam_type_id in BaseBeamType.plugins.valid_ids: #@UndefinedVariable
        for mode in modes:
            yield check_find_best_root, beam_type_id, mode

def check_find_best_root(beam_type_id, mode):
    beam_type = BaseBeamType.coerce(beam_type_id) #@UndefinedVariable
    
    _, mu_m_error = find_best_root(
        beam_type,
        mode,
        t.DECIMAL_PRECISION,
        include_error=True,
        use_cache=False
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
        for beam_type in BaseBeamType.plugins.instances: #@UndefinedVariable
            _, mu_m_error = find_best_root(
                beam_type,
                mode,
                decimal_precision,
                include_error=True,
                use_cache=False
            )
            
            # Special case for this mode, don't check the `mu_m_error`
            if mode in beam_type.dont_improve_mu_m_for_modes:
                continue
            
            assert_less_equal(mu_m_error, t.MAX_ERROR_TOLERANCE)
