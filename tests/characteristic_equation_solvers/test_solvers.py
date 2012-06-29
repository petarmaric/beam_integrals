from nose.plugins.skip import SkipTest
from beam_integrals.beam_types import coerce_beam_type, VALID_BEAM_TYPE_IDS
from beam_integrals.characteristic_equation_solvers import find_best_root
from tests import MAX_ERROR_TOLERANCE, MAX_MODE, DECIMAL_PRECISION
from tests.tools import assert_less_equal #@UnresolvedImport


def test_find_best_root():
    modes = range(1, MAX_MODE+1)
    for beam_type_id in VALID_BEAM_TYPE_IDS:
        for mode in modes:
            yield check_find_best_root, beam_type_id, mode

def check_find_best_root(beam_type_id, mode):
    beam_type = coerce_beam_type(beam_type_id)
    
    _, mu_m_error = find_best_root(
        beam_type,
        mode,
        DECIMAL_PRECISION,
        include_error=True,
    )
    
    # Special case for this mode, don't check the `mu_m_error`
    if mode in beam_type.dont_improve_mu_m_for_modes:
        raise SkipTest
    
    assert_less_equal(mu_m_error, MAX_ERROR_TOLERANCE)
