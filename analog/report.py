"""Analog log report object."""
from collections import Counter, defaultdict, OrderedDict
import textwrap

import numpy


__all__ = ('Report',)


class ListStats(object):

    """Statistic analysis of a list of values.

    Provides the mean, median and 90th, 75th and 25th percentiles.

    """

    def __init__(self, elements):
        """Calculate some stats from list of values.

        :param elements: list of values.
        :type elements: ``list``

        """
        self.mean = numpy.mean(elements) if elements else None
        self.median = numpy.median(elements) if elements else None
        self.perc90 = numpy.percentile(elements, 90) if elements else None
        self.perc75 = numpy.percentile(elements, 75) if elements else None
        self.perc25 = numpy.percentile(elements, 25) if elements else None

    def stats(self):
        """Generate pretty representation of list statistics object.

        :returns: statistic report.
        :rtype: ``str``

        """
        return textwrap.dedent("""\
            {self.mean:>10.5}   mean
            {self.median:>10.5}   median
            {self.perc90:>10.5}   90th percentile
            {self.perc75:>10.5}   75th percentile
            {self.perc25:>10.5}   25th percentile
            """).format(self=self)


class Report:

    """Log analysis report object.

    Provides these statistical metrics:

    * Number for requests.
    * Response status code distribution.
    * Request path distribution.
    * Response time statistics (mean, median, 90th, 75th and 25th percentiles).
    * Response upstream time statistics (as above).
    * Response body size in bytes statistics (as above).
    * Per path request method (HTTP verb) distribution.
    * Per path response status code distribution.
    * Per path response time statistics (as above).
    * Per path response upstream time statistics (as above).
    * Per path response body size in bytes statistics (as above).

    """

    def __init__(self):
        self.requests = 0
        self._status = Counter()
        self._paths = Counter()
        self._times = []
        self._upstream_times = []
        self._body_bytes = []
        self._path_verbs = defaultdict(Counter)
        self._path_status = defaultdict(Counter)
        self._path_times = defaultdict(list)
        self._path_upstream_times = defaultdict(list)
        self._path_body_bytes = defaultdict(list)

    @property
    def status(self):
        """List status codes of all matched requests, ordered by frequency.

        :returns: tuples of status code and occurrency count.
        :rtype: ``list`` of ``tuple``

        """
        return self._status.most_common()

    @property
    def paths(self):
        """List paths of all matched requests, ordered by frequency.

        :returns: tuples of path and occurrency count.
        :rtype: ``list`` of ``tuple``

        """
        return self._paths.most_common()

    @property
    def times(self):
        """Response time statistics of all matched requests.

        :returns: response time statistics.
        :rtype: :py:class:`analog.report.ListStats`

        """
        return ListStats(self._times)

    @property
    def upstream_times(self):
        """Response upstream time statistics of all matched requests.

        :returns: response upstream time statistics.
        :rtype: :py:class:`analog.report.ListStats`

        """
        return ListStats(self._upstream_times)

    @property
    def body_bytes(self):
        """Response body size in bytes of all matched requests.

        :returns: response body size statistics.
        :rtype: :py:class:`analog.report.ListStats`

        """
        return ListStats(self._body_bytes)

    @property
    def path_verbs(self):
        """List request methods (HTTP verbs) of all matched requests per path.

        Verbs are grouped by path and ordered by frequency.

        :returns: path mapping of tuples of verb and occurrency count.
        :rtype: ``dict`` of ``list`` of ``tuple``

        """
        return OrderedDict(
            sorted(((path, counter.most_common())
                    for path, counter in self._path_verbs.items()),
                   key=lambda item: item[0]))

    @property
    def path_status(self):
        """List status codes of all matched requests per path.

        Status codes are grouped by path and ordered by frequency.

        :returns: path mapping of tuples of status code and occurrency count.
        :rtype: ``dict`` of ``list`` of ``tuple``

        """
        return OrderedDict(
            sorted(((path, counter.most_common())
                    for path, counter in self._path_status.items()),
                   key=lambda item: item[0]))

    @property
    def path_times(self):
        """Response time statistics of all matched requests per path.

        :returns: path mapping of response time statistics.
        :rtype: ``dict`` of :py:class:`analog.report.ListStats`

        """
        return OrderedDict(
            sorted(((path, ListStats(values))
                    for path, values in self._path_times.items()),
                   key=lambda item: item[0]))

    @property
    def path_upstream_times(self):
        """Response upstream time statistics of all matched requests per path.

        :returns: path mapping of response upstream time statistics.
        :rtype: ``dict`` of :py:class:`analog.report.ListStats`

        """
        return OrderedDict(
            sorted(((path, ListStats(values))
                    for path, values in self._path_upstream_times.items()),
                   key=lambda item: item[0]))

    @property
    def path_body_bytes(self):
        """Response body size in bytes of all matched requests per path.

        :returns: path mapping of body size statistics.
        :rtype: ``dict`` of :py:class:`analog.report.ListStats`

        """
        return OrderedDict(
            sorted(((path, ListStats(values))
                    for path, values in self._path_body_bytes.items()),
                   key=lambda item: item[0]))

    def _str_path_counts(self, path_counts):
        return "\n".join("{count:>10,}   {key}".format(
            key=key, count=count) for key, count in path_counts)

    def _indent(self, text, indent=4):
        lines = []
        for idx, line in enumerate(text.splitlines()):
            space = " " * indent if idx > 0 else ""
            lines.append(space + line)
        return "\n".join(lines)

    def stats(self):
        """Generate overall analysis summary report.

        :returns: statistics report.
        :rtype: ``str``

        """
        if self.requests == 0:
            return "Zero requests analyzed."

        return textwrap.dedent("""\
            Requests: {self.requests}

            Status Codes:
                {status}

            Paths:
                {paths}

            Times [s]:
                {times}

            Upstream Times [s]:
                {upstream_times}

            Body Bytes Sent [B]:
                {body_bytes}
            """).format(
            self=self,
            status=self._indent(self._str_path_counts(self.status)),
            paths=self._indent(self._str_path_counts(self.paths)),
            times=self._indent(self.times.stats()),
            upstream_times=self._indent(self.upstream_times.stats()),
            body_bytes=self._indent(self.body_bytes.stats()))

    def path_stats(self):
        """Generate per path analysis summary report.

        :returns: per path statistics report.
        :rtype: ``str``

        """
        if self.requests == 0:
            return "Zero requests analyzed."

        path_stats = []
        for path, verbs, status, times, upstream_times, body_bytes in zip(
                self.path_verbs.keys(),
                self.path_verbs.values(),
                self.path_status.values(),
                self.path_times.values(),
                self.path_upstream_times.values(),
                self.path_body_bytes.values()):

            path_stats.append(textwrap.dedent("""\
                {path}

                    HTTP Verbs:
                        {verbs}

                    Status Codes:
                        {status}

                    Times [s]:
                        {times}

                    Upstream Times [s]:
                        {upstream_times}

                    Body Bytes Sent [B]:
                        {body_bytes}
                """).format(
                path=path,
                verbs=self._indent(self._str_path_counts(verbs), 8),
                status=self._indent(self._str_path_counts(status), 8),
                times=self._indent(times.stats(), 8),
                upstream_times=self._indent(upstream_times.stats(), 8),
                body_bytes=self._indent(body_bytes.stats(), 8)))
        return "\n".join(path_stats)
