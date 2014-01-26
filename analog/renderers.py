"""Analog log report renderers."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import abc
import csv
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import textwrap

from tabulate import tabulate

from analog.exceptions import UnknownRendererError
from analog.utils import PrefixMatchingCounter


def find_subclasses(cls, _seen=None):
    """Find all subclasses (recursively) of ``cls``.

    :param cls: class object.
    :param _seen: set of already found classes if called recursively.
    :returns: generator of ``cls`` subclasses.
    :rtype: ``generator``

    """
    if _seen is None:
            _seen = set()
    for subclass in cls.__subclasses__():
        if subclass not in _seen:
            _seen.add(subclass)
            yield subclass
            for subclass in find_subclasses(subclass, _seen):
                yield subclass


class Renderer(object):

    """Base report renderer interface."""

    __metaclass__ = abc.ABCMeta

    name = None

    @abc.abstractmethod
    def render(self, report, path_stats=False):
        """Render report statistics.

        :param report: log analysis report object.
        :type report: :py:class:`analog.report.Report`
        :param path_stats: include per path statistics in output.
        :type path_stats: ``bool``
        :returns: output string
        :rtype: `str`

        """

    @classmethod
    def all_renderers(cls):
        """Get a mapping of all defined report renderer names.

        :returns: dictionary of name to renderer class.
        :rtype: ``dict``

        """
        return {subclass.name: subclass for subclass in find_subclasses(cls)
                if subclass.name is not None}

    @classmethod
    def by_name(cls, name):
        """Select specific ``Renderer`` subclass by name.

        :param name: name of subclass.
        :type name: ``str``
        :returns: ``Renderer`` subclass instance.
        :rtype: :py:class:`analog.renderers.Renderer`
        :raises: :py:class:`analog.exceptions.UnknownRendererError` for unknown
            subclass names.

        """
        renderers = cls.all_renderers()
        if name in renderers:
            return renderers[name]()
        raise UnknownRendererError(name)


class PlainTextRenderer(Renderer):

    """Default renderer for plain text output in list format."""

    name = "plain"

    def render(self, report, path_stats=False):
        """
        Render overall analysis summary report.

        :returns: output string
        :rtype: `str`

        """
        if report.requests == 0:
            return "Zero requests analyzed."

        output = textwrap.dedent("""\
            Requests: {self.requests}

            HTTP Verbs:
                {verbs}

            Status Codes:
                {status}

            Path Requests:
                {paths}

            Times [s]:
                {times}

            Upstream Times [s]:
                {upstream_times}

            Body Bytes Sent [B]:
                {body_bytes}
            """).format(
            self=report,
            verbs=self._indent(self._str_path_counts(report.verbs)),
            status=self._indent(self._str_path_counts(report.status)),
            paths=self._indent(self._str_path_counts(report.path_requests)),
            times=self._indent(self._render_list_stats(report.times)),
            upstream_times=self._indent(
                self._render_list_stats(report.upstream_times)),
            body_bytes=self._indent(
                self._render_list_stats(report.body_bytes)))

        if path_stats:
            output += "\n" + self._render_path_stats(report)

        return output

    def _render_path_stats(self, report):
        """
        Render per path analysis summary report.

        :returns: output string
        :rtype: `str`

        """
        if report.requests == 0:
            return "Zero requests analyzed."

        output = []
        for path, verbs, status, times, upstream_times, body_bytes in zip(
                report.path_verbs.keys(),
                report.path_verbs.values(),
                report.path_status.values(),
                report.path_times.values(),
                report.path_upstream_times.values(),
                report.path_body_bytes.values()):

            output.append(textwrap.dedent("""\
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
                times=self._indent(self._render_list_stats(times), 8),
                upstream_times=self._indent(
                    self._render_list_stats(upstream_times), 8),
                body_bytes=self._indent(
                    self._render_list_stats(body_bytes), 8)))

        return "\n".join(output)

    def _render_list_stats(self, list_stats):
        """
        Generate pretty representation of list statistics object.

        :param list_stats: ``ListStats`` instance.
        :returns: statistic report.
        :rtype: ``str``

        """
        return textwrap.dedent("""\
            {stats.mean:>10.5}   mean
            {stats.median:>10.5}   median
            {stats.perc90:>10.5}   90th percentile
            {stats.perc75:>10.5}   75th percentile
            {stats.perc25:>10.5}   25th percentile
            """).format(stats=list_stats)

    def _str_path_counts(self, path_counts):
        """
        Render path count.

        :returns: output string
        :rtype: `str`

        """
        return "\n".join("{count:>10,}   {key}".format(
            key=key, count=count) for key, count in path_counts)

    def _indent(self, text, indent=4):
        """
        Render every line after the first line indented.

        Example::

            line1
                line2
                line3

        :returns: output string
        :rtype: `str`

        """
        lines = []
        for idx, line in enumerate(text.splitlines()):
            space = " " * indent if idx > 0 else ""
            lines.append(space + line)
        return "\n".join(lines)


class TabularDataRenderer(Renderer):

    """Base renderer for report output in any tabular form."""

    __metaclass__ = abc.ABCMeta

    #: field names for ``ListStats`` attributes
    _stats_fields = ('times', 'upstream_times', 'body_bytes')
    #: attribute names of ``ListStats`` attributes
    _list_stats_keys = ("mean", "median", "perc90", "perc75", "perc25")

    def _list_stats(self, list_stats):
        """Get list of (key,value) tuples for each attribute of ``list_stats``.

        :param list_stats: list statistics object.
        :type list_stats: :py:class:`analog.report.ListStats`
        :returns: (key, value) tuples for each ``ListStats`` attribute.
        :rtype: ``list`` of ``tuple``

        """
        return zip(self._list_stats_keys,
                   [list_stats.mean, list_stats.median,
                    list_stats.perc90, list_stats.perc75, list_stats.perc25])

    def _tabular_data(self, report, path_stats):
        """Prepare tabular data for output.

        Generate a list of header fields, a list of total values for each field
        and a list of the same values per path.

        :param report: log analysis report object.
        :type report: :py:class:`analog.report.Report`
        :param path_stats: include per path statistics in output.
        :type path_stats: ``bool``
        :returns: tuple of table (headers, rows).
        :rtype: ``tuple``

        """
        # sorted list of all HTTP verbs in this report and their counts
        verb_names, verb_counts = zip(*sorted(
            (verb, count) for (verb, count) in report.verbs))
        # sorted list of all status codes in this report and their counts
        status_names, status_counts = zip(*sorted(
            (str(status), count)
            for (status, count) in report.status))
        # all statistical attributes of the report
        stats = [(stats_field, self._list_stats(getattr(report, stats_field)))
                 for stats_field in self._stats_fields]
        stats_names, stats_values = zip(*(
            ('{0}_{1}'.format(field, analysis), value)
            for (field, list_stats) in stats
            for (analysis, value) in list_stats))

        status_headers = tuple("status_{code:x<3}".format(code=code)
                               for code in status_names)

        headers = (("path", "requests") + verb_names + status_headers
                   + stats_names)
        total = (("total", report.requests) +
                 verb_counts + status_counts + stats_values)

        rows = []
        # include path statistics?
        if path_stats:
            # get per path values from report, ordered by path
            for (path, verbs, status, times, utimes, body_bytes) in zip(
                    report.path_verbs.keys(),
                    report.path_verbs.values(),
                    report.path_status.values(),
                    report.path_times.values(),
                    report.path_upstream_times.values(),
                    report.path_body_bytes.values()):
                requests = report._path_requests[path]
                verbs = dict(verbs)
                status = PrefixMatchingCounter(dict(status))
                row = [path, requests]
                row += [verbs.get(name, 0) for name in verb_names]
                row += [status.get(name, 0) for name in status_names]
                row += [time[1] for time in self._list_stats(times)]
                row += [utime[1] for utime in self._list_stats(utimes)]
                row += [bbytes[1] for bbytes in self._list_stats(body_bytes)]
                rows.append(row)

        rows.append(total)

        return (list(headers), rows)


class ASCIITableRenderer(TabularDataRenderer):

    """Base renderer for report output in ascii-table format."""

    __metaclass__ = abc.ABCMeta

    tabulate_format = None

    def render(self, report, path_stats=False):
        """Render report statistics using ``tabulate``.

        :param report: log analysis report object.
        :type report: :py:class:`analog.report.Report`
        :param path_stats: include per path statistics in output.
        :type path_stats: ``bool``
        :returns: output string
        :rtype: `str`

        """
        headers, rows = self._tabular_data(report, path_stats)
        return tabulate(rows,
                        headers=headers,
                        tablefmt=self.tabulate_format,
                        floatfmt='.3f')


class SimpleTableRenderer(ASCIITableRenderer):

    """Renderer for tabular report output in simple reSt table format."""

    name = "table"
    tabulate_format = 'rst'


class GridTableRenderer(ASCIITableRenderer):

    """Renderer for tabular report output in grid table format."""

    name = "grid"
    tabulate_format = 'grid'


class SeparatedValuesRenderer(TabularDataRenderer):

    """Base renderer for report output in delimiter-separated values format."""

    __metaclass__ = abc.ABCMeta

    #: value delimter. E.g. comma or tab.
    delimiter = None

    def render(self, report, path_stats):
        """Render report statistics using a CSV writer.

        :param report: log analysis report object.
        :type report: :py:class:`analog.report.Report`
        :param path_stats: include per path statistics in output.
        :type path_stats: ``bool``
        :returns: output string
        :rtype: `str`

        """
        headers, rows = self._tabular_data(report, path_stats)

        stream = StringIO()
        writer = csv.writer(stream, delimiter=str(self.delimiter))
        writer.writerow(headers)
        writer.writerows(rows)

        return stream.getvalue()[:-1]  # Do not return last newline


class CSVRenderer(SeparatedValuesRenderer):

    """Renderer for report output in comma separated values format."""

    name = 'csv'
    delimiter = ','


class TSVRenderer(SeparatedValuesRenderer):

    """Renderer for report output in tab separated values format."""

    name = 'tsv'
    delimiter = '\t'
