from nose.tools import eq_
from nose_extra_tools import assert_in #@UnresolvedImport
from beam_integrals.integrals import BaseIntegral


def test_parent_id():
    for id in BaseIntegral.plugins.valid_ids: #@ReservedAssignment @UndefinedVariable
        yield check_parent_id, id

def check_parent_id(id): #@ReservedAssignment
    cls = BaseIntegral.plugins.id_to_class[id] #@UndefinedVariable
    if cls.parent_id():
        parent_cls = BaseIntegral.plugins.id_to_class[cls.parent_id()] #@UndefinedVariable
        # Can't use `issubclass()` for this check as `issubclass(cls, cls)`
        # returns `True` and need to make sure `cls` can't be its own parent
        # integral
        assert_in(parent_cls, cls.__bases__) 
    else:
        # Make sure a parentless integral isn't inheriting any other integrals
        superclasses = set(cls.__mro__[1:]) # `cls.__mro__[0] is cls`
        assert superclasses.isdisjoint(BaseIntegral.plugins.classes) #@UndefinedVariable

def test_has_parent():
    for id in BaseIntegral.plugins.valid_ids: #@ReservedAssignment @UndefinedVariable
        yield check_has_parent, id

def check_has_parent(id): #@ReservedAssignment
    cls = BaseIntegral.plugins.id_to_class[id] #@UndefinedVariable
    eq_(cls.has_parent(), cls.parent_id() is not None)
