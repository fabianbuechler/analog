"""Analog log report renderers."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import abc
import textwrap

from analog.exceptions import UnknownRendererError


class Renderer(object):

    """Base report renderer interface."""

    @abc.abstractmethod
    def render(self):
        """Render overall report statistics."""

    @abc.abstractmethod
    def _render_path_stats(self):
        """Render per path report statistics."""

    def _render_list_stats(self, elements):
        """Render list statistics."""

    @classmethod
    def all_renderers(cls):
        """Get a list fo all defined report renderer names.

        :returns: names of all renderers.
        :rtype: ``list``

        """
        return [subclass.name for subclass in cls.__subclasses__()]

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
        for subclass in cls.__subclasses__():
            if subclass.name == name:
                return subclass()
        raise UnknownRendererError(name)


class PlainTextRenderer(Renderer):

    """ Default renderer. """

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
