"""Test the analog.utils module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime
import sys
import tempfile
try:
    from unittest import mock
except ImportError:
    import mock

from analog import analyzer


PY3 = sys.version_info[0] == 3
TMPFILE_ARGS = {} if not PY3 else {'encoding': 'utf-8'}


def test_analyze(capsys):
    """``analyze`` is a quick entry point utility to the ``Analyzer`` class."""
    mock_report = mock.MagicMock()
    # mock_report.execution_time = 0.4
    with mock.patch('analog.analyzer.Analyzer',
                    return_value=mock_report) as mock_analyzer:

        log = tempfile.TemporaryFile(mode='w', **TMPFILE_ARGS)
        log.write('2014-03-15T12:00:00 GET /me/a/cookie')

        analyzer.analyze(log=log, format='nginx')

    # passed the logfile to an Analyzer instance
    mock_analyzer.assert_called_once_with(
        log=log, format='nginx', pattern=None, time_format=None,
        verbs=analyzer.DEFAULT_VERBS,
        status_codes=analyzer.DEFAULT_STATUS_CODES,
        paths=analyzer.DEFAULT_PATHS, max_age=None, path_stats=False)
    assert mock_report.mock_calls[:2] == [
        # analyzer was executed to retreve a report
        mock.call(),
        # timing was printed
        # mock.call().execution_time.__str__,
        # report.render called
        mock.call().render(path_stats=False, output_format=None),
    ]


class TestAnalyzer():

    """Test ``analog.analyzer.Analyzer`` implementation."""

    def setup(self):
        """Define analyzer for Analyzer tests."""
        self.log = tempfile.TemporaryFile(mode='w', **TMPFILE_ARGS)
        self.log.write(
            '123.123.123.123 - test_client [16/Jan/2014:13:30:30 +0000] '
            '"POST /auth/token HTTP/1.1" 200 174 "-" '
            '"OAuthClient 0.2.3" "-" 0.633 0.633')
        self.log.write(
            '234.234.234.234 - - [17/Jan/2014:12:00:27 +0000] '
            '"GET /sub/folder HTTP/1.1" 200 110 "-" '
            '"UAString" "-" 0.312 0.312')
        self.analyzer = analyzer.Analyzer(
            log=self.log, format='nginx', pattern=None, time_format=None,
            verbs=analyzer.DEFAULT_VERBS,
            status_codes=analyzer.DEFAULT_STATUS_CODES,
            paths=analyzer.DEFAULT_PATHS, max_age=None, path_stats=False)

    def test_monitor_path(self):
        """Full paths are converted to monitored paths."""
        with mock.patch.object(self.analyzer, '_pathconf',
                               ['/foo/bar', '/auth']):
            assert self.analyzer._monitor_path('/auth/token') == '/auth'
            assert self.analyzer._monitor_path('/foo') is None
            assert self.analyzer._monitor_path('/foo/bar/baz') == '/foo/bar'

        # if no paths are defined, all pathes will be monitored as is
        with mock.patch.object(self.analyzer, '_pathconf', []):
            assert self.analyzer._monitor_path('/auth/token') == '/auth/token'
            assert self.analyzer._monitor_path('/foo') == '/foo'
            assert self.analyzer._monitor_path('/foo/bar/baz') == '/foo/bar/baz'

    def test_timestamp(self):
        """Timestamp strings from log entries can be converted to datetimes."""
        assert (self.analyzer._timestamp('16/Jan/2014:13:30:30 +0000') ==
                datetime.datetime(2014, 1, 16, 13, 30, 30))

    # def test_custom_format(self):
    #     """Initializing an Analyzer with custom log format."""
    #     # this is essentially the nginx pattern and time format
    #     pattern = r'''
    #         ^(?P<remote_addr>\S+)\s-\s(?P<remote_user>\S+)\s
    #         \[(?P<timestamp>.*?)\]\s
    #         "(?P<verb>[A-Z]+)\s(?P<path>[^?]+)(?:\?.+)?\sHTTP/(?:[\d.]+)"\s
    #         (?P<status>\d+?)\s
    #         (?P<body_bytes_sent>\d+?)\s
    #         "(?P<http_referer>[^"]+?)"\s
    #         "(?P<http_user_agent>[^"]+?)"\s
    #         "(?P<http_x_forwarded_for>[^"]+?)"\s
    #         (?P<request_time>[\d\.]+)\s
    #         (?P<upstream_response_time>[\d\.]+)\s?
    #         (?P<pipe>\S+)?$'''
    #     time_format = '%d/%b/%Y:%H:%M:%S +0000'

    #     analyzer.Analyzer(
    #         log=self.log, format='custom',
    #         pattern=pattern, time_format=time_format,
    #         verbs=analyzer.DEFAULT_VERBS,
    #         status_codes=analyzer.DEFAULT_STATUS_CODES,
    #         paths=analyzer.DEFAULT_PATHS, max_age=None, path_stats=False)
