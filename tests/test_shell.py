import mock
from nose_extra_tools import assert_raises #@UnresolvedImport
import beam_integrals as b
from beam_integrals import characteristic_equation_solvers as ces
from beam_integrals.exceptions import ShellCommandError
from beam_integrals.shell import Shell


def setup():
    global shell, _shell
    _shell = Shell()
    shell = lambda cmd: _shell.main(cmd.split())

def test_help():
    @mock.patch.object(_shell.parser, 'print_help')
    def test_help(m):
        shell('help')
        m.assert_called_with()
        
    @mock.patch.object(_shell.parser, 'print_help')
    def test_help_no_args(m):
        shell('')
        m.assert_called_with()
        
    @mock.patch.object(_shell.subcommands['best-roots-of-characteristic-equations-regenerate-cache'], 'print_help')
    def test_help_best_roots_of_characteristic_equations_regenerate_cache(m):
        shell('help best-roots-of-characteristic-equations-regenerate-cache')
        m.assert_called_with()
    
    test_help()
    test_help_no_args()
    test_help_best_roots_of_characteristic_equations_regenerate_cache()
    
    assert_raises(ShellCommandError, shell, 'help invalid-command')

@mock.patch.object(ces.best_roots_cache, 'regenerate')
def test_best_roots_of_characteristic_equations_regenerate_cache(m):
    shell('best-roots-of-characteristic-equations-regenerate-cache')
    m.assert_called_with(max_mode=b.DEFAULT_MAX_MODE, decimal_precision=b.DEFAULT_DECIMAL_PRECISION)
    
    shell('best-roots-of-characteristic-equations-regenerate-cache --max-mode=10 --decimal-precision=15')
    m.assert_called_with(max_mode=10, decimal_precision=15)
