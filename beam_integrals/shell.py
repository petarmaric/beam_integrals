# Based on `python-openstack` and its `openstack.compute.shell` module
import argparse
import sys
import beam_integrals as b
from beam_integrals import characteristic_equation_solvers as ces
from beam_integrals.exceptions import ShellCommandError


# Decorator for argparse args
def arg(*args, **kwargs):
    def _decorator(func):
        # Because of the sematics of decorator composition if we just append
        # to the options list positional options will appear to be backwards
        func.__dict__.setdefault('arguments', []).insert(0, (args, kwargs))
        return func
    return _decorator


class Shell(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog='beam_integrals',
            description='Determines beam integrals of all 6 supported beam '\
                        'types, as described in D.D. Milasinovic, "The Finite '\
                        'Strip Method in Computational Mechanics" (ISBN 8680297194)',
            epilog='See "beam_integrals help COMMAND" for help on a specific command',
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        
        # Global arguments
        self.parser.add_argument('-h', '--help',
            action='help',
            help= argparse.SUPPRESS,
        )
        self.parser.add_argument('--version',
            action='version',
            version="%(prog)s " + b.__version__
        )
        
        # Subcommands
        subparsers = self.parser.add_subparsers(metavar='<subcommand>')
        self.subcommands = {}
        
        # Everything that's do_* is a subcommand
        for attr in (a for a in dir(self) if a.startswith('do_')):
            # I prefer to be hypen-separated instead of underscores
            command = attr[3:].replace('_', '-')
            callback = getattr(self, attr)
            desc = callback.__doc__ or ''
            help = desc.strip() #@ReservedAssignment
            arguments = getattr(callback, 'arguments', [])
            
            subparser = subparsers.add_parser(command,
                help=help,
                description=desc,
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter
            )
            subparser.add_argument('-h', '--help',
                action='help',
                help=argparse.SUPPRESS,
            )
            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)
    
    def main(self, argv=None):
        argv = argv if argv is not None else sys.argv[1:]
        
        # Show help if called without any arguments
        if not argv:
            self.parser.print_help()
            return 0
        
        # Parse args and call whatever callback was selected
        args = self.parser.parse_args(argv)
        
        # Short-circuit and deal with help right away
        if args.func == self.do_help:
            self.do_help(args)
            return 0
        
        args.func(args)
    
    @arg('command', metavar='<subcommand>', nargs='?', help='Display help for <subcommand>')
    def do_help(self, args):
        """Display help about this program or one of its subcommands"""
        if args.command:
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise ShellCommandError("'%s' is not a valid subcommand" % args.command)
        else:
            self.parser.print_help()
    
    @arg('--max-mode', metavar='<mode>', type=int, default=b.DEFAULT_MAX_MODE, help='Maximum mode')
    @arg('--decimal-precision', metavar='<precision>', type=int, default=b.DEFAULT_DECIMAL_PRECISION, help='Decimal precision')
    def do_best_roots_of_characteristic_equations_regenerate_cache(self, args):
        """
        Regenerate the best roots of characteristic equations cache, for all
        supported beam types
        """
        ces.best_roots_cache.regenerate(
            max_mode=args.max_mode,
            decimal_precision=args.decimal_precision
        )


def main(): #pragma: no cover
    try:
        Shell().main()
    except ShellCommandError, e:
        print >> sys.stderr, e
        sys.exit(1)

if __name__ == '__main__':
    main()
