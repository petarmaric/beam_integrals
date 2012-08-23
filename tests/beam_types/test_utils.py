from nose.tools import eq_
from beam_integrals.beam_types import BaseBeamType


ID_TO_STR_REPR = {
    1: 'Simply Supported Beam (id=1)',
    2: 'Clamped Clamped Beam (id=2)',
    3: 'Clamped Free Beam (id=3)',
    4: 'Clamped Simply Supported Beam (id=4)',
    5: 'Simply Supported Free Beam (id=5)',
    6: 'Free Free Beam (id=6)',
}

ID_TO_FILENAME = {
    1: '1-simply-supported-beam',
    2: '2-clamped-clamped-beam',
    3: '3-clamped-free-beam',
    4: '4-clamped-simply-supported-beam',
    5: '5-simply-supported-free-beam',
    6: '6-free-free-beam',
}

ID_TO_CHARACTERISTIC_EQUATION_STR_REPR = {
    1: 'sin(mu_m) = 0',
    2: 'cos(mu_m)*cosh(mu_m) - 1 = 0',
    3: 'cos(mu_m)*cosh(mu_m) + 1 = 0',
    4: 'tan(mu_m) - tanh(mu_m) = 0',
    5: 'tan(mu_m) - tanh(mu_m) = 0',
    6: 'cos(mu_m)*cosh(mu_m) - 1 = 0',
}


def test_str_repr():
    for id in BaseBeamType.plugins.valid_ids: #@ReservedAssignment @UndefinedVariable
        yield check_str_repr, id

def check_str_repr(id): #@ReservedAssignment
    eq_(ID_TO_STR_REPR[id], str(BaseBeamType.plugins.id_to_instance[id])) #@UndefinedVariable

def test_filename():
    for id in BaseBeamType.plugins.valid_ids: #@ReservedAssignment @UndefinedVariable
        yield check_filename, id

def check_filename(id): #@ReservedAssignment
    eq_(ID_TO_FILENAME[id], BaseBeamType.plugins.id_to_instance[id].filename) #@UndefinedVariable

def test_characteristic_equation_str_repr():
    for id in BaseBeamType.plugins.valid_ids: #@ReservedAssignment @UndefinedVariable
        yield check_characteristic_equation_str_repr, id

def check_characteristic_equation_str_repr(id): #@ReservedAssignment
    eq_(
        ID_TO_CHARACTERISTIC_EQUATION_STR_REPR[id],
        BaseBeamType.plugins.id_to_instance[id].characteristic_equation_str #@UndefinedVariable
    )
