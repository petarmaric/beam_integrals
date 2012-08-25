from nose.tools import eq_
from beam_integrals import characteristic_equation_solvers as ces


SOLVER_NAME_TO_CLASS = {
    'anderson': ces.AndersonRootfinder,
    'illinois': ces.IllinoisRootfinder,
    'pegasus': ces.PegasusRootfinder,
    'secant': ces.SecantRootfinder,
}


def test_solver_name():
    for name in ces.BaseRootfinder.plugins.valid_ids: #@UndefinedVariable
        yield check_solver_name, name

def check_solver_name(name):
    eq_(
        SOLVER_NAME_TO_CLASS[name],
        ces.BaseRootfinder.plugins.id_to_class[name] #@UndefinedVariable
    )
