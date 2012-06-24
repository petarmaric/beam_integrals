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

ID_TO_FILENAME = {
    1: '1-simply-supported-beam',
    2: '2-clamped-clamped-beam',
    3: '3-clamped-free-beam',
    4: '4-clamped-simply-supported-beam',
    5: '5-simply-supported-free-beam',
    6: '6-free-free-beam',
}


def test_str_repr():
    for id in bt.VALID_BEAM_TYPE_IDS: #@ReservedAssignment
        yield check_str_repr, id

def check_str_repr(id): #@ReservedAssignment
    eq_(ID_TO_STR_REPR[id], str(bt.ID_TO_BEAM_TYPE_INSTANCE[id]))

def test_filename():
    for id in bt.VALID_BEAM_TYPE_IDS: #@ReservedAssignment
        yield check_filename, id

def check_filename(id): #@ReservedAssignment
    eq_(ID_TO_FILENAME[id], bt.ID_TO_BEAM_TYPE_INSTANCE[id].filename)
