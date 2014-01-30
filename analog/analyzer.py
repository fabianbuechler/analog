"""Analog analysis module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime
import re
import time

from analog.exceptions import MissingFormatError
from analog.formats import LogFormat
from analog.report import Report


#: Default verbs to monitor if unconfigured.
DEFAULT_VERBS = ['DELETE', 'GET', 'PATCH', 'POST', 'PUT']
#: Default status codes to monitor if unconfigured.
DEFAULT_STATUS_CODES = [1, 2, 3, 4, 5]
#: Default paths (all) to monitor if unconfigured.
DEFAULT_PATHS = []


class Analyzer:

    """Log analysis utility.

    Scan a logfile for logged requests and analyze calculate statistical
    metrics in a :py:class:`analog.report.Report`.

    """

    def __init__(self, log, format,
                 verbs=DEFAULT_VERBS, status_codes=DEFAULT_STATUS_CODES,
                 paths=DEFAULT_PATHS, max_age=None, path_stats=False):
        """Configure log analyzer.

        :param log: handle on logfile to read and analyze.
        :type log: :py:class:`io.TextIOWrapper`
        :param format: log format identifier or regex pattern.
        :type format: ``str``
        :param verbs: HTTP verbs to be tracked.
            Defaults to :py:data:`analog.analyzer.DEFAULT_VERBS`.
        :type verbs: ``list``
        :param status_codes: status_codes to be tracked. May be prefixes,
            e.g. ["100", "2", "3", "4", "404" ].
            Defaults to :py:data:`analog.analyzer.DEFAULT_STATUS_CODES`.
        :type status_codes: ``list``
        :param paths: Paths to explicitly analyze. If not defined, paths are
            detected automatically.
            Defaults to :py:data:`analog.analyzer.DEFAULT_PATHS`.
        :type paths: ``list`` of ``str``
        :param max_age: Max. age of log entries to analyze in minutes.
            Unlimited by default.
        :type max_age: ``int``
        :raises: :py:class:`analog.exceptions.MissingFormatError` if no
            ``format`` is specified.

        """
        self._log = log
        if not format:
            raise MissingFormatError(
                "Require log format. Specify format name or regex pattern.")
        formats = LogFormat.all_formats()
        if format in formats:
            self._format = formats[format]
        else:
            self._format = LogFormat('custom', re.escape(format))
        self._verbs = verbs
        self._status_codes = status_codes
        self._pathconf = paths

        self._max_age = max_age

        # execution time
        self.execution_time = None

    def _monitor_path(self, path):
        """Convert full request path to monitored path.

        If no path groups are configured to be monitored, all full paths are.

        :param path: the full request path.
        :type path: ``str``
        :returns: the monitored path (part of ``path``) or ``None`` if not
            monitored.
        :rtype: ``str`` or ``None``

        """
        if not self._pathconf:
            return path
        for monitored in self._pathconf:
            if path.startswith(monitored):
                return monitored
        return None

    def _timestamp(self, time_str):
        """Convert timestamp strings from nginx to datetime objects.

        Format is "15/Jan/2014:14:12:50 +0000".

        :returns: request timestamp datetime.
        :rtype: :py:class:`datetime.datetime`

        """
        return datetime.datetime.strptime(time_str, self._format.time_format)

    def __call__(self):
        """Analyze defined logfile.

        :returns: log analysis report object.
        :rtype: :py:class:`analog.report.Report`

        """
        if self._max_age is not None:
            self._now = datetime.datetime.now()
            self._now = self._now.replace(second=0, microsecond=0)
            self._min_time = (
                self._now - datetime.timedelta(minutes=self._max_age))

        # start timestamp
        started = time.clock()

        report = Report(self._verbs, self._status_codes)

        # read lines from logfile for the last max_age minutes
        for line in self._log:
            # parse line
            match = self._format.pattern.search(line)
            if match is None:
                continue
            log_entry = self._format.entry(match)

            if self._max_age is not None:
                # don't process anything older than max_age
                timestamp = self._timestamp(log_entry.timestamp)
                if timestamp < self._min_time:
                    continue
                # stop processing when now was reached
                if timestamp > self._now:
                    break

            # parse request
            path = self._monitor_path(log_entry.path)
            if path is None:
                continue

            # collect the numbers
            report.add(
                path=path,
                verb=log_entry.verb,
                status=int(log_entry.status),
                time=float(log_entry.request_time),
                upstream_time=float(log_entry.upstream_response_time),
                body_bytes=int(log_entry.body_bytes_sent))

        # end timestamp
        finished = time.clock()
        report.execution_time = finished - started

        return report


def analyze(log, format, verbs=DEFAULT_VERBS, status_codes=DEFAULT_STATUS_CODES,
            paths=DEFAULT_PATHS, max_age=None, path_stats=False, timing=False,
            output_format=None):
    """Convenience wrapper around :py:class:`analog.analyzer.Analyzer`.

    :param log: handle on logfile to read and analyze.
    :type log: :py:class:`io.TextIOWrapper`
    :param format: log format identifier or regex pattern.
    :type format: ``str``
    :param verbs: HTTP verbs to be tracked.
        Defaults to :py:data:`analog.analyzer.DEFAULT_VERBS`.
    :type verbs: ``list``
    :param status_codes: status_codes to be tracked. May be prefixes,
        e.g. ["100", "2", "3", "4", "404" ].
        Defaults to :py:data:`analog.analyzer.DEFAULT_STATUS_CODES`.
    :type status_codes: ``list``
    :param paths: Paths to explicitly analyze. If not defined, paths are
        detected automatically.
        Defaults to :py:data:`analog.analyzer.DEFAULT_PATHS`.
    :type paths: ``list`` of ``str``
    :param max_age: Max. age of log entries to analyze in minutes.
        Unlimited by default.
    :type max_age: ``int``
    :param path_stats: Print per-path analysis report. Default off.
    :type path_stats: ``bool``
    :param timing: print analysis timing information?
    :type timing: ``bool``
    :param output_format: report output format.
    :type output_format: ``str``

    :returns: log analysis report object.
    :rtype: :py:class:`analog.report.Report`

    """
    analyzer = Analyzer(log=log, format=format,
                        verbs=verbs, status_codes=status_codes,
                        paths=paths, max_age=max_age, path_stats=path_stats)
    report = analyzer()

    # print timing information
    if timing:
        print("Analyzed logs in {elapsed:.3f}s.\n".format(
            elapsed=report.execution_time))

    # print report in requested output format
    print(report.render(path_stats=path_stats, output_format=output_format))

    return report
