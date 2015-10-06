from nose.tools import eq_
from nose_extra_tools import assert_raises #@UnresolvedImport
from beam_integrals.beam_types import BaseBeamType
from beam_integrals.exceptions import UnableToGuessScaleFunctionError
from beam_integrals.integrals import BaseIntegral
from . import test_integration as helper
import tests as t


def test_scale_factor_same_for_all_modes():
    for integral_id in BaseIntegral.plugins.valid_ids: #@UndefinedVariable
        integral = BaseIntegral.coerce(integral_id) #@UndefinedVariable
        
        # Skip integrals with parents, as they behave the same
        if integral.has_parent():
            continue
        
        for beam_type in BaseBeamType.plugins.instances_sorted_by_id: #@UndefinedVariable
            variables = list(helper.iterate_over_used_variables(integral))[-1]
            expected_scale_factor = integral.guess_scale_factor(beam_type, *variables)
            
            for m, t, v, n in helper.iterate_over_used_variables(integral):
                yield check_scale_factor_same_for_all_modes, integral_id,\
                      beam_type.id, m, t, v, n, expected_scale_factor

def check_scale_factor_same_for_all_modes(integral_id, beam_type_id, m, t, v, n, expected_scale_factor):
    integral = BaseIntegral.coerce(integral_id) #@UndefinedVariable
    beam_type = BaseBeamType.coerce(beam_type_id) #@UndefinedVariable
    
    # Special case for these modes due to the mode-specific boundary condition
    if set([m, t, v, n]) & set(beam_type.dont_improve_mu_m_for_modes):
        with assert_raises(UnableToGuessScaleFunctionError):
            integral.guess_scale_factor(beam_type, m, t, v, n)
        
        return
        
    eq_(integral.guess_scale_factor(beam_type, m, t, v, n), expected_scale_factor)
