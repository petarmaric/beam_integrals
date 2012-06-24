from nose.tools import raises
from beam_integrals import beam_types as bt
from beam_integrals.exceptions import InvalidBeamTypeError, PerformanceWarning
from tests.tools import assert_is, issues_warnings #@UnresolvedImport


class TestBeamTypeCoercion(object):
    def setup(self):
        self.actual_beam_type_class = bt.SimplySupportedBeam
        self.desired_beam_type_id = 1
        
        self.desired_beam_type_instance = bt.ID_TO_BEAM_TYPE_INSTANCE[
            self.desired_beam_type_id
        ]
        self.desired_beam_type_class = type(self.desired_beam_type_instance)
    
    @issues_warnings(PerformanceWarning)
    def test_valid_beam_type_instance(self):
        assert_is(
            type(bt.coerce_beam_type(self.actual_beam_type_class())),
            self.desired_beam_type_class
        )
    
    @issues_warnings(PerformanceWarning)
    def test_valid_beam_type_class(self):
        assert_is(
            type(bt.coerce_beam_type(self.actual_beam_type_class)),
            self.desired_beam_type_class
        )
    
    def test_valid_beam_type_id(self):
        assert_is(
            bt.coerce_beam_type(self.desired_beam_type_id),
            self.desired_beam_type_instance
        )
    
    @raises(InvalidBeamTypeError)
    def test_invalid_beam_type_id(self):
        bt.coerce_beam_type(-1)
    
    @raises(InvalidBeamTypeError)
    def test_unknown_type(self):
        bt.coerce_beam_type(object())
