from nose.tools import eq_
from beam_integrals import beam_types as bt


ID_TO_STR_REPR = {
    1: 'Simply Supported Beam (id=1)',
    2: 'Clamped Clamped Beam (id=2)',
    3: 'Clamped Free Beam (id=3)',
    4: 'Clamped Simply Supported Beam (id=4)',
    5: 'Simply Supported Free Beam (id=5)',
    6: 'Free Free Beam (id=6)',
}


def test_str_repr():
    for id in bt.VALID_BEAM_TYPE_IDS: #@ReservedAssignment
        yield check_str_repr, id

def check_str_repr(id): #@ReservedAssignment
    eq_(ID_TO_STR_REPR[id], str(bt.ID_TO_BEAM_TYPE_INSTANCE[id]))
