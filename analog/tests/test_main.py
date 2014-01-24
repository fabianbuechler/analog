"""Test the analog.main module and CLI."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
try:
    from unittest import mock
except ImportError:
    import mock

import pytest

import analog


@pytest.fixture
def tmp_logfile(tmpdir):
    """Fixture creating a temporary logfile.

    :returns: local tempfile object.

    """
    log_name = 'logmock.log'
    logfile = tmpdir.join(log_name)
    logfile.write("log entry #1")
    return logfile


def test_help(capsys):
    """analog --help prints help and describes arguments."""
    with pytest.raises(SystemExit):
        analog.main(['analog', '--help'])
        out, err = capsys.readouterr()

        # main docstring is used as help description
        assert analog.main.__doc__ in out

        # analog arguments are listed
        assert '--config' in out
        assert '--version' in out
        assert '--format' in out
        assert '--regex' in out
        assert '--max-age' in out
        assert '--print-stats' in out
        assert '--print-path-stats' in out


def test_format_or_regex_required(capsys, tmp_logfile):
    """analog requires log --format or pattern --regex."""
    with pytest.raises(SystemExit) as exit:
        analog.main(['analog', str(tmp_logfile)])
        assert exit.errisinstance(analog.MissingFormatError)


@mock.patch('analog.analyze', return_value=analog.Report([], []))
def test_paths(mock_analyze, capsys, tmp_logfile):
    """analog --path specifies paths to monitor."""
    with pytest.raises(SystemExit):
        # the --path argument can be specified multiple times, also as -p
        analog.main(['analog',
                     '--format', 'nginx',
                     '--config', '/foo/bar',
                     str(tmp_logfile)])
        mock_analyze.assert_called_once_with(
            log=mock.ANY,
            format='nginx',
            config='/foo/bar',
            max_age=10,
            print_stats=False,
            print_path_stats=False)
