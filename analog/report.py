"""Analog log report object."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from collections import Counter, defaultdict, OrderedDict

from analog.renderers import Renderer
from analog.utils import PrefixMatchingCounter


class ListStats(object):

    """Statistic analysis of a list of values.

    Provides the mean, median and 90th, 75th and 25th percentiles.

    """

    def __init__(self, elements):
        """Calculate some stats from list of values.

        :param elements: list of values.
        :type elements: ``list``

        """
        import numpy
        self.mean = numpy.mean(elements) if elements else None
        self.median = numpy.median(elements) if elements else None
        self.perc90 = numpy.percentile(elements, 90) if elements else None
        self.perc75 = numpy.percentile(elements, 75) if elements else None
        self.perc25 = numpy.percentile(elements, 25) if elements else None


class Report(object):

    """Log analysis report object.

    Provides these statistical metrics:

    * Number for requests.
    * Response request method (HTTP verb) distribution.
    * Response status code distribution.
    * Requests per path.
    * Response time statistics (mean, median, 90th, 75th and 25th percentiles).
    * Response upstream time statistics (as above).
    * Response body size in bytes statistics (as above).
    * Per path request method (HTTP verb) distribution.
    * Per path response status code distribution.
    * Per path response time statistics (as above).
    * Per path response upstream time statistics (as above).
    * Per path response body size in bytes statistics (as above).

    """

    def __init__(self, verbs, status_codes):
        """Create new log report object.

        Use ``add()`` method to add log entries to be analyzed.

        :param verbs: HTTP verbs to be tracked.
        :type verbs: ``list``
        :param status_codes: status_codes to be tracked. May be prefixes,
            e.g. ["100", "2", "3", "4", "404" ]
        :type status_codes: ``list``
        :returns: Report analysis object
        :rtype: :py:class:`analog.report.Report`

        """

        def status_counter():
            return PrefixMatchingCounter(
                {str(code): 0 for code in status_codes})

        self.execution_time = None
        self.requests = 0
        self._verbs = Counter({verb: 0 for verb in verbs})
        self._status = status_counter()
        self._times = []
        self._upstream_times = []
        self._body_bytes = []
        self._path_requests = Counter()
        self._path_verbs = defaultdict(Counter)
        self._path_status = defaultdict(status_counter)
        self._path_times = defaultdict(list)
        self._path_upstream_times = defaultdict(list)
        self._path_body_bytes = defaultdict(list)

    def add(self, path, verb, status, time, upstream_time, body_bytes):
        """Add a log entry to the report.

        :param path: monitored request path.
        :type path: ``str``
        :param verb: HTTP method (GET, POST, ...)
        :type verb: ``str``
        :param status: response status code.
        :type status: ``int``
        :param time: response time in seconds.
        :type time: ``float``
        :param upstream_time: upstream response time in seconds.
        :type upstream_time: ``float``
        :param body_bytes: response body size in bytes.
        :type body_bytes: ``float``

        """
        self.requests += 1
        if verb in self._verbs:  # Only keep verbs that are being tracked
            self._verbs[verb] += 1
        self._status.inc(str(status))
        self._times.append(time)
        self._upstream_times.append(upstream_time)
        self._body_bytes.append(body_bytes)
        self._path_requests[path] += 1
        self._path_verbs[path][verb] += 1
        self._path_status[path].inc(status)
        self._path_times[path].append(time)
        self._path_upstream_times[path].append(upstream_time)
        self._path_body_bytes[path].append(body_bytes)

    @property
    def verbs(self):
        """List request methods of all matched requests, ordered by frequency.

        :returns: tuples of HTTP verb and occurrency count.
        :rtype: ``list`` of ``tuple``

        """
        return self._verbs.most_common()

    @property
    def status(self):
        """List status codes of all matched requests, ordered by frequency.

        :returns: tuples of status code and occurrency count.
        :rtype: ``list`` of ``tuple``

        """
        return self._status.most_common()

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
    def path_requests(self):
        """List paths of all matched requests, ordered by frequency.

        :returns: tuples of path and occurrency count.
        :rtype: ``list`` of ``tuple``

        """
        return self._path_requests.most_common()

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

    def render(self, path_stats, output_format):
        """Render report data into ``output_format``.

        :param path_stats: include per path statistics in output.
        :type path_stats: ``bool``
        :param output_format: name of report renderer.
        :type output_format: ``str``
        :raises: :py:class:`analog.exceptions.UnknownRendererError` or unknown
            ``output_format`` identifiers.
        :returns: rendered report data.
        :rtype: ``str``

        """
        renderer = Renderer.by_name(name=output_format)
        return renderer.render(self, path_stats=path_stats)
