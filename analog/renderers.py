"""Analog log report renderers."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import abc
from collections import OrderedDict
import itertools
import textwrap

from tabulate import tabulate

from analog.exceptions import UnknownRendererError


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

    @abc.abstractmethod
    def render(self):
        """Render report statistics."""

    @classmethod
    def all_renderers(cls):
        """Get a mapping of all defined report renderer names.

        :returns: dictionary of name to renderer class.
        :rtype: ``dict``

        """
        return {subclass.name: subclass for subclass in find_subclasses(cls)}

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

            Paths:
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
            paths=self._indent(self._str_path_counts(report.paths)),
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


class SimpleTableRenderer(Renderer):

    """Renderer for tabular report output in simple reSt table format."""

    name = "table"
    tabulate_format = 'rst'

    def _order_counter(self, counter):
        """Order (key, count) tuples of a ``counter`` by key.

        :param counter: ``(key, count)`` tuples list as returned by
            :py:meth:`collections.Counter.most_common`.
        :type counter: ``list`` of ``tuple``
        :returns: counter, ordered by ``key``.
        :rtype: ``list`` of ``tuple``

        """
        return sorted(counter, key=lambda item: item[0])

    def _fill_missing(self, all_keys, counter, default=0):
        """Add missing keys to ``counter`` according to ``all_keys``.

        Missing keys will be set to ``default``.

        :param all_keys: list of all required keys.
        :type all_keys: ``list``
        :param counter: ``(key, count)`` tuples list as returned by
            :py:meth:`collections.Counter.most_common`.
        :type counter: ``list`` of ``tuple``
        :param default: value for missing keys.
        :type default: any
        :returns: counter, filled with ``default`` for missing keys.
        :rtype: ``list`` of ``tuple``

        """
        counter_dict = dict(counter)
        filled = OrderedDict()
        for key in all_keys:
            if key in counter_dict:
                filled[key] = counter_dict[key]
            else:
                filled[key] = default
        return filled.items()

    def render(self, report, path_stats=False):
        """
        Render overall analysis summary report.

        :returns: output string
        :rtype: `str`

        """
        if report.requests == 0:
            return "Zero requests analyzed."

        # all rows need equal columns, so save headers
        all_verbs = []
        all_status = []

        # table headers
        headers = ["Path", "Requests"]
        overall = ["ALL", report.requests]
        report_verbs = self._order_counter(report.verbs)
        for verb, count in report_verbs:
            all_verbs.append(verb)
            headers.append("Verb[{0}]".format(verb.upper()))
            overall.append(count)
        report_status = self._order_counter(report.status)
        for status, count in report_status:
            all_status.append(status)
            headers.append("Status[{0}]".format(status))
            overall.append(count)
        for field, analysis in itertools.product(
                # field header, field
                (("Time", report.times),
                 ("Upstream Time", report.upstream_times),
                 ("Body Bytes", report.body_bytes)),
                # analysis header, analysis attribute
                (("mean", 'mean'),
                 ("median", 'median'),
                 ("90th perc", 'perc90'),
                 ("75th perc", 'perc75'),
                 ("25th perc", 'perc25'))):
            headers.append("{0}[{1}]".format(field[0], analysis[0]))
            overall.append(getattr(field[1], analysis[1]))

        # prepare data for tabular output as 2-dimensional list
        rows = []

        # per path report
        report_paths = self._order_counter(report.paths)
        if path_stats:
            paths_verbs = report.path_verbs
            paths_status = report.path_status
            paths_times = report.path_times
            paths_upstream_times = report.path_upstream_times
            paths_body_bytes = report.path_body_bytes
            for path, requests in report_paths:
                row = [path, requests]
                path_verbs = self._fill_missing(all_verbs, paths_verbs[path])
                for verb, count in path_verbs:
                    row.append(count)
                path_status = self._fill_missing(all_status, paths_status[path])
                for status, count in path_status:
                    row.append(count)
                for field, analysis in itertools.product(
                        (paths_times[path],
                         paths_upstream_times[path],
                         paths_body_bytes[path]),
                        ("mean", "median", "perc90", "perc75", "perc25")):
                    row.append(getattr(field, analysis))

                rows.append(row)

        # overall report is last line
        rows.append(overall)

        # send to tabulate to generate table output
        return tabulate(rows,
                        headers=headers,
                        tablefmt=self.tabulate_format,
                        floatfmt=".3f")


class GridTableRenderer(SimpleTableRenderer):

    """Renderer for tabular report output in grid table format."""

    name = "grid"
    tabulate_format = 'grid'
