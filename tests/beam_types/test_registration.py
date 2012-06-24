from beam_integrals import beam_types as bt
from tests.tools import assert_equal #@UnresolvedImport


def test_id_to_beam_type_class():
    assert_equal(
        dict((cls.id, cls) for cls in bt.BaseBeamType.plugins), #@UndefinedVariable
        bt.ID_TO_BEAM_TYPE_CLASS
    )

def test_all_beam_types_classes():
    assert_equal(bt.BaseBeamType.plugins, bt.ALL_BEAM_TYPES_CLASSES) #@UndefinedVariable

def test_id_to_beam_type_instance():
    assert_equal(
        dict((cls.id, cls) for cls in bt.BaseBeamType.plugins), #@UndefinedVariable
        dict((id, type(obj)) for id, obj in bt.ID_TO_BEAM_TYPE_INSTANCE.items()), #@ReservedAssignment
    )

def test_all_beam_types_instances():
    assert_equal(
        bt.BaseBeamType.plugins, #@UndefinedVariable
        [type(obj) for obj in bt.ALL_BEAM_TYPE_INSTANCES]
    )

def test_valid_beam_type_ids():
    assert_equal(
        [cls.id for cls in bt.BaseBeamType.plugins], #@UndefinedVariable
        bt.VALID_BEAM_TYPE_IDS
    )
