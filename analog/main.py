"""Analog console entry point."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import argparse
import sys
import textwrap

import analog


def main(argv=None):
    """
    analog - Log Analysis Utility.

    Name the logfile to analyze (positional argument) or leave it out to read
    from ``stdin``. This can be handy for piping in filtered logfiles (e.g. with
    ``grep``).

    To analyze for the logfile for specified paths, provide them via ``--path``
    arguments (mutliple times) or list the paths in a file and point analog at
    it using ``--pathconf``.

    Paths are to be defined as the beginnings of the paths you want to monitor.
    For example, specifying ``/some/path`` will group all requests those path
    starts with this value. If no paths are specified they will be grouped
    automatically.

    Predefined logfile formats can be selected with ``--format``. To specify a
    custom format, pass a regular expression with named groups for log entry
    attributes as ``--regex`` argument.

    To print a general report, pass ``--print-stats``, or for a more detailed,
    per-path report specify ``--print-path-stats``.

    """
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(main.__doc__.replace('``', "'")),
        formatter_class=argparse.RawDescriptionHelpFormatter)

    # either -p / --path (multiple times) or -c / --config path-config file
    pathargs = parser.add_mutually_exclusive_group()
    # -p / --path
    pathargs.add_argument('-p', '--path', action='append', dest='paths',
                          help="paths to monitor")
    # -c / --config
    pathargs.add_argument('-c', '--pathconf', action='store',
                          type=argparse.FileType('r'),
                          help="path config file")
    # -v / --version
    parser.add_argument('--version', action='version',
                        version="analog {v}".format(v=analog.__version__))
    # logfile, defaults to stdin
    parser.add_argument('log', action='store', nargs='?',
                        type=argparse.FileType('r'), default='-',
                        help="logfile to analyze. "
                             "Defaults to stdin for piping.")
    # either -f / --format or -r / --regex for format name or expression
    formatargs = parser.add_mutually_exclusive_group()
    # -f / --format
    formatargs.add_argument('-f', '--format', action='store',
                            choices=analog.LogFormat.all_formats(),
                            help="Log format")

    # -o / --output
    formatargs.add_argument('-o', '--output', action='store',
                            dest='output_format',
                            choices=analog.Renderer.all_renderers(),
                            help="Output format")
    # -r / --regex
    formatargs.add_argument('-r', '--regex', action='store',
                            help='Regex format pattern with named groups.')
    # -a / --max-age
    parser.add_argument('-a', '--max-age', action='store', type=int,
                        default=analog.Analyzer.MAX_AGE,
                        help="Analyze logs until n minutes age.")
    # -s / --stats
    parser.add_argument('-ps', '--path-stats', action='store_true',
                        help="include statistics per path")

    try:
        if argv is None:
            argv = sys.argv
        args = parser.parse_args(argv[1:])

        # paths config from args, config file or automatic detection
        if args.paths:
            paths = args.paths
        elif args.pathconf:
            paths = args.pathconf.read().splitlines()
        else:
            paths = []

        report = analog.analyze(log=args.log,
                                format=args.format or args.regex,
                                paths=paths,
                                max_age=args.max_age,
                                path_stats=args.path_stats)
        report.render(output_format=args.output_format)
        parser.exit(0)

    except KeyboardInterrupt:
        parser.exit(1, "\nExecution cancelled.")
