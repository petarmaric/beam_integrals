from nose.tools import raises
from sympy import Float
from beam_integrals.beam_types import BaseBeamType
from beam_integrals.characteristic_equation_solvers import AndersonRootfinder
from beam_integrals.exceptions import MultipleRootsError, UndefinedRootError


class TestExceptions(object):
    def setup(self):
        self.undefined_root_error_mode = 1
        self.multiple_roots_error_mode = 2
        
        class FakeBeam(BaseBeamType):
            id = -1 #@ReservedAssignment
            characteristic_function = Float(0)
            
            dont_improve_mu_m_for_modes = (self.undefined_root_error_mode,)
            
            def mu_m_initial_guess(self, mode):
                return Float(mode)
        
        self.beam_type = FakeBeam()
        self.rootfinder = AndersonRootfinder()
    
    def teardown(self):
        type(self.beam_type)._unregister_plugin() #@UndefinedVariable
        
    @raises(UndefinedRootError)
    def test_undefined_root_error(self):
        self.rootfinder.x0(self.beam_type, self.undefined_root_error_mode)
    
    @raises(MultipleRootsError)
    def test_multiple_roots_error(self):
        self.rootfinder.x0(self.beam_type, self.multiple_roots_error_mode)
