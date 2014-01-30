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

    To analyze for the logfile for specified paths, provide them via ``--path``
    arguments (mutliple times). Also, monitoring specifig HTTP verbs (request
    methods) via ``--verb`` and specific response status codes via ``--status``
    argument(s) is possible.

    Paths and status codes all match the start of the actual log entry values.
    Thus, specifying a path ``/foo`` will group all paths beginning with that
    value.

    Predefined logfile formats can be selected with ``--format``. To specify a
    custom format, pass a regular expression with named groups for log entry
    attributes as ``--regex`` argument.

    Arguments can be listed in a file by specifying ``@argument_file.txt`` as
    parameter.

    """
    parser = AnalogArgumentParser(
        description=textwrap.dedent(main.__doc__.replace('``', "'")),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        fromfile_prefix_chars='@')

    format_choices = analog.LogFormat.all_formats()
    output_choices = analog.Renderer.all_renderers().keys()

    # --version
    parser.add_argument('--version',
                        action='version',
                        version="analog {v}".format(v=analog.__version__))
    # either -f / --format or -r / --regex for format name or expression
    formatargs = parser.add_mutually_exclusive_group()
    # -f / --format
    formatargs.add_argument('-f', '--format',
                            action='store',
                            dest='format',
                            default=None,
                            choices=format_choices,
                            help="Log format")
    # -r / --regex
    formatargs.add_argument('-r', '--regex',
                            action='store',
                            help='regex format pattern with named groups.')
    # -o / --output_format
    parser.add_argument('-o', '--output-format',
                        action='store',
                        dest='output_format',
                        default='plain',
                        choices=output_choices,
                        help="output format")
    # -p / --path
    parser.add_argument('-p', '--path',
                        action='append',
                        dest='paths',
                        default=DEFAULT_PATHS,
                        help="paths to monitor (repeat for multiple)")
    # -v / --verb
    parser.add_argument('-v', '--verb',
                        action='append',
                        dest='verbs',
                        default=DEFAULT_VERBS,
                        help="verbs to monitor (repeat for multiple)")
    # -s / --status
    parser.add_argument('-s', '--status',
                        action='append',
                        dest='status_codes',
                        default=DEFAULT_STATUS_CODES,
                        help="status codes to monitor (repeat for multiple)")
    # -a / --max_age
    parser.add_argument('-a', '--max_age',
                        action='store',
                        type=int,
                        default=None,
                        help="analyze logs until n minutes age")
    # -ps / --path_stats
    parser.add_argument('-ps', '--path-stats',
                        action='store_true',
                        dest='path_stats',
                        help="include statistics per path")
    # -t / --timing
    parser.add_argument('-t', '--timing',
                        action='store_true',
                        help="print timing")
    # logfile, defaults to stdin
    parser.add_argument('log',
                        action='store',
                        nargs='?',
                        type=argparse.FileType('r'),
                        default='-',
                        help="logfile to analyze."
                             "Defaults to stdin for piping.")

    try:
        if argv is None:
            argv = sys.argv
        args = parser.parse_args(argv[1:])

        # analyze logfile and generate report
        analog.analyze(log=args.log,
                       format=args.format or args.regex,
                       paths=args.paths,
                       verbs=args.verbs,
                       status_codes=args.status_codes,
                       max_age=args.max_age,
                       path_stats=args.path_stats,
                       timing=args.timing,
                       output_format=args.output_format)

        parser.exit(0)

    except analog.AnalogError as exc:
        parser.error(str(exc))

    except KeyboardInterrupt:
        parser.exit(1, "\nExecution cancelled.")


def _option_invalid_choice(option, value, choices):
    """Error message for invalid choices of ini config options.

    :param option: name of configuration option
    :type option: ``str``
    :param value: user-provided configuration value
    :param value: ``str``
    :param choices: valid option value choices
    :type choices: ``list``
    :returns: error message
    :rtype: ``str``

    """
    return ("config option {option}: invalid choice {value!r} (choose from "
            "{choices})".format(option=option, value=value,
                                choices=", ".join(map(repr, choices))))


def _option_mutually_exclusive(option1, option2):
    """Error message for mutually exclusive config options specified together.

    :param option1: name of first option
    :type option1: ``str``
    :param option2: name of second option
    :type option2: ``str``
    :returns: error message
    :rtype: ``str``

    """
    return ("config option {option2} not allowed with "
            "option {option1}".format(option1=option1, option2=option2))
