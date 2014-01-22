from __future__ import print_function
import textwrap


class Renderer(object):
    """ Base class for renderers """

    def __init__(self, report):
        self._report = report

    def render_stats(self):
        raise NotImplementedError

    def render_path_stats(self):
        raise NotImplementedError


class PlainTextRenderer(Renderer):
    """ Default renderer """

    def render_stats(self):
        """Render overall analysis summary report.

        """
        report = self._report
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

    def render_path_stats(self):
        """Render per path analysis summary report.


        """
        report = self._report

        if report.requests == 0:
            return "Zero requests analyzed."

        path_stats = []
        for path, verbs, status, times, upstream_times, body_bytes in zip(
                report.path_verbs.keys(),
                report.path_verbs.values(),
                report.path_status.values(),
                report.path_times.values(),
                report.path_upstream_times.values(),
                report.path_body_bytes.values()):

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
        print("\n".join(path_stats))

    def _str_path_counts(self, path_counts):
        return "\n".join("{count:>10,}   {key}".format(
            key=key, count=count) for key, count in path_counts)

    def _indent(self, text, indent=4):
        lines = []
        for idx, line in enumerate(text.splitlines()):
            space = " " * indent if idx > 0 else ""
            lines.append(space + line)
        return "\n".join(lines)
