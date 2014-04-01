"""Test the analog.utils module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from collections import Counter
import os
import tempfile
import textwrap

from analog import utils


def test_analog_argument_parser():
    """Analog uses a custom argumentparser.

    It accepts comma/whitespace separated arguments when reading from a file.

    """
    parser = utils.AnalogArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('-p', '--path', action='append')
    parser.add_argument('-f', '--flag', action='store_true')
    parser.add_argument('-s', '--status', action='append')
    parser.add_argument('-v', '--verb', action='append')
    parser.add_argument('file', action='store')

    argfile = tempfile.NamedTemporaryFile(delete=False)
    with open(argfile.name, 'w') as fp:
        fp.write(textwrap.dedent('''\
            -p=/foo/bar
            --path /baz/bum
            --flag
            -s=200 400 500
            --verb GET, POST, PUT
            somefile.log
            '''))

    args = parser.parse_args(['@' + argfile.name])
    assert args.path == ['/foo/bar', '/baz/bum']
    assert args.flag is True
    assert args.status == ['200', '400', '500']
    assert args.verb == ['GET', 'POST', 'PUT']
    assert args.file == 'somefile.log'

    os.unlink(argfile.name)


def test_prefix_matching_counter():
    """PrefixMatchingCounter is a Counter that matches string prefixes."""
    pmc = utils.PrefixMatchingCounter({'2': 0, '40': 0})
    assert isinstance(pmc, Counter)

    pmc.inc(200)
    pmc.inc(206)
    pmc.inc(200)
    pmc.inc(404)
    pmc.inc(409)
    pmc.inc(400)

    pmc.inc(302)
    pmc.inc(419)
    pmc.inc(499)

    assert pmc['2'] == 3
    assert pmc['40'] == 3
