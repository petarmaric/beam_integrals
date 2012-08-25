from nose.tools import eq_
from beam_integrals.integrals import BaseIntegral


def id_to_str(id): #@ReservedAssignment
    return "I%d" % id

def test_str_repr():
    for id in BaseIntegral.plugins.valid_ids: #@ReservedAssignment @UndefinedVariable
        yield check_str_repr, id

def check_str_repr(id): #@ReservedAssignment
    eq_(id_to_str(id), str(BaseIntegral.plugins.id_to_instance[id])) #@UndefinedVariable
