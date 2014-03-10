"""Analog console entry point."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import argparse
import sys
import textwrap

import analog
from analog.analyzer import DEFAULT_VERBS, DEFAULT_STATUS_CODES, DEFAULT_PATHS
from analog.utils import AnalogArgumentParser


def main(argv=None):
    """
    analog - Log Analysis Utility.

    Name the logfile to analyze (positional argument) or leave it out to read
    from ``stdin``. This can be handy for piping in filtered logfiles
    (e.g. with ``grep``).

    Select the logfile format subcommand that suits your needs or define a
    custom log format using ``analog custom --pattern-regex <...> --time-format
    <...>``.

    To analyze for the logfile for specified paths, provide them via ``--path``
    arguments (mutliple times). Also, monitoring specifig HTTP verbs (request
    methods) via ``--verb`` and specific response status codes via ``--status``
    argument(s) is possible.

    Paths and status codes all match the start of the actual log entry values.
    Thus, specifying a path ``/foo`` will group all paths beginning with that
    value.

    Arguments can be listed in a file by specifying ``@argument_file.txt`` as
    parameter.

    """
    parser = AnalogArgumentParser(
        description=textwrap.dedent(main.__doc__.replace('``', "'")),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        fromfile_prefix_chars='@')

    format_choices = analog.LogFormat.all_formats()
    output_choices = sorted(analog.Renderer.all_renderers().keys())

    # --version
    parser.add_argument('--version',
                        action='version',
                        version="analog {v}".format(v=analog.__version__))

    # common arguments
    common = argparse.ArgumentParser(add_help=False)

    # -o / --output_format
    common.add_argument('-o', '--output-format',
                        action='store',
                        dest='output_format',
                        default='plain',
                        choices=output_choices,
                        help="output format")
    # -p / --path
    common.add_argument('-p', '--path',
                        action='append',
                        dest='paths',
                        default=DEFAULT_PATHS,
                        help="paths to monitor (repeat for multiple)")
    # -v / --verb
    common.add_argument('-v', '--verb',
                        action='append',
                        dest='verbs',
                        default=DEFAULT_VERBS,
                        help="verbs to monitor (repeat for multiple)")
    # -s / --status
    common.add_argument('-s', '--status',
                        action='append',
                        dest='status_codes',
                        default=DEFAULT_STATUS_CODES,
                        help="status codes to monitor (repeat for multiple)")
    # -a / --max_age
    common.add_argument('-a', '--max-age',
                        action='store',
                        type=int,
                        default=None,
                        help="analyze logs until n minutes age")
    # -ps / --path_stats
    common.add_argument('-ps', '--path-stats',
                        action='store_true',
                        dest='path_stats',
                        help="include statistics per path")
    # -t / --timing
    common.add_argument('-t', '--timing',
                        action='store_true',
                        help="print timing")
    # logfile, defaults to stdin
    common.add_argument('log',
                        action='store',
                        nargs='?',
                        type=argparse.FileType('r'),
                        default='-',
                        help="logfile to analyze."
                             "Defaults to stdin for piping.")

    # subcommands for predefined log formats
    format_parsers = parser.add_subparsers(
        title="log format",
        description="analyze logfiles of a certain format",
        metavar='FORMAT',
        dest='format')
    for format in format_choices:
        format_parsers.add_parser(format, parents=[common],
                                  help="{} log format".format(format))

    # subcommand for custom log format
    custom_format = format_parsers.add_parser('custom', parents=[common],
                                              help="custom log format")
    # -pr / --pattern-regex
    custom_format.add_argument('-pr', '--pattern-regex',
                               action='store',
                               dest='pattern',
                               required=True,
                               help='regex format pattern with named groups.')
    # -tf / --time-format
    custom_format.add_argument('-tf', '--time-format',
                               action='store',
                               dest='time_format',
                               required=True,
                               help='timestamp format (strftime compatible)')

    try:
        if argv is None:  # pragma: no cover
            argv = sys.argv
        args = parser.parse_args(argv[1:])

        format_kwargs = {'format': args.format}
        if args.format == 'custom':
            format_kwargs.update({
                'pattern': args.pattern,
                'time_format': args.time_format,
            })

        # analyze logfile and generate report
        analog.analyze(log=args.log,
                       paths=args.paths,
                       verbs=args.verbs,
                       status_codes=args.status_codes,
                       max_age=args.max_age,
                       path_stats=args.path_stats,
                       timing=args.timing,
                       output_format=args.output_format,
                       **format_kwargs)

        parser.exit(0)

    except analog.AnalogError as exc:
        parser.error(str(exc))

    except KeyboardInterrupt:
        parser.exit(1, "\nExecution cancelled.")
