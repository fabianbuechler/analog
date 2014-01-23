"""Analog log report renderers."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import abc
import textwrap

from analog.exceptions import UnknownRendererError


class Renderer(object):

    """Base report renderer interface."""

    @abc.abstractmethod
    def render_stats(self):
        """Render overall report statistics."""

    @abc.abstractmethod
    def render_path_stats(self):
        """Render per path report statistics."""

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
    """ Default renderer """

    name = "plain"

    def render(self, report, path_stats=False):
        """Render overall analysis summary report.

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
            times=self._indent(report.times.stats()),
            upstream_times=self._indent(report.upstream_times.stats()),
            body_bytes=self._indent(report.body_bytes.stats()))

        print(output)
        if path_stats:
            self.render_path_stats(report)

    def render_path_stats(self, report):
        """Render per path analysis summary report.


        """

        if report.requests == 0:
            return "Zero requests analyzed."

        for path, verbs, status, times, upstream_times, body_bytes in zip(
                report.path_verbs.keys(),
                report.path_verbs.values(),
                report.path_status.values(),
                report.path_times.values(),
                report.path_upstream_times.values(),
                report.path_body_bytes.values()):

            print(textwrap.dedent("""\
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

    def _str_path_counts(self, path_counts):
        return "\n".join("{count:>10,}   {key}".format(
            key=key, count=count) for key, count in path_counts)

    def _indent(self, text, indent=4):
        lines = []
        for idx, line in enumerate(text.splitlines()):
            space = " " * indent if idx > 0 else ""
            lines.append(space + line)
        return "\n".join(lines)
