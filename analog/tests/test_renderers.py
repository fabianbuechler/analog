"""Test the analog.renderers module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
try:
    from unittest import mock
except ImportError:
    import mock

import pytest

from analog import renderers
from analog import Report
from analog.exceptions import UnknownRendererError


class TestRendererBase():

    """The ``Renderer`` baseclass provides utilities for renderer lookup."""

    def test_all_renderers(self):
        """For a list of available renderers, use ``Renderer.all_renderers``."""
        all_renderers = renderers.Renderer.all_renderers()
        assert sorted(all_renderers) == sorted(
            ['plain', 'grid', 'table', 'csv', 'tsv'])

    def test_renderer_by_name(self):
        """Use ``Renderer.by_name`` to retrieve a specific renderer."""
        renderer = renderers.Renderer.by_name('plain')
        assert isinstance(renderer, renderers.PlainTextRenderer)

    def test_unknown_renderer(self):
        """``UnknownRendererError`` is raised for unknown renderer names."""
        with pytest.raises(UnknownRendererError):
            renderers.Renderer.by_name('unknown')

    def test_renderer_abstract(self):
        """``Renderer`` is an abstract baseclass and cannot be used directly."""
        with pytest.raises(TypeError) as exc:
            renderers.Renderer()
        assert exc.exconly() == ("TypeError: Can't instantiate abstract class "
                                 "Renderer with abstract methods render")


class TestRenderers():

    """Test different available report renderers."""

    def setup(self):
        """Define report for renderer tests."""
        self.report = Report(verbs=['GET', 'POST', 'PATCH'],
                             status_codes=['2', '4', '5'])
        self.report.add(path='/foo/bar/1', verb='GET', status=200,
                        time=0.1, upstream_time=0.09, body_bytes=255)
        self.report.add(path='/foo/bar/1', verb='GET', status=200,
                        time=0.1, upstream_time=0.09, body_bytes=255)
        self.report.add(path='/foo/bar', verb='POST', status=200,
                        time=0.12, upstream_time=0.12, body_bytes=402)
        self.report.add(path='/foo/bar', verb='POST', status=409,
                        time=0.21, upstream_time=0.20, body_bytes=23)
        self.report.add(path='/foo/bar', verb='GET', status=200,
                        time=0.23, upstream_time=0.22, body_bytes=212)
        self.report.add(path='/foo/bar/1', verb='PATCH', status=200,
                        time=0.1, upstream_time=0.1, body_bytes=320)
        self.report.add(path='/foo/bar/1', verb='POST', status=404,
                        time=0.1, upstream_time=0.1, body_bytes=0)
        self.report.add(path='/foo/bar/1', verb='POST', status=404,
                        time=0.1, upstream_time=0.1, body_bytes=0)
        self.report.add(path='/foo/bar/1', verb='POST', status=200,
                        time=0.2, upstream_time=0.2, body_bytes=123)

    def read(self, path):
        """Return should-be output from test output dir."""
        output = ''
        with open(os.path.abspath(os.path.join(
                os.path.dirname(__file__), 'output', path + '.txt'))) as fp:
            output = fp.read()
        return output

    def test_renderer_output(self):
        """Make sure renderer output look alright."""
        for output_format in sorted(renderers.Renderer.all_renderers().keys()):
            output = self.report.render(
                path_stats=True, output_format=output_format)
            expected = self.read(output_format)
            assert output == expected

    def test_svrenderer_py27_stringio(self):
        """Handle that StringIO does not accept newline arg on Python 2.7."""
        csvrenderer = renderers.CSVRenderer()
        csvrenderer.render

        # StringIO has newline argument in Python3.3
        with mock.patch('analog.renderers.StringIO') as mock_stringio:
            csvrenderer.render(report=self.report, path_stats=False)
            mock_stringio.assert_called_once_with(newline='')

        # but not in Python2.7
        try:
            with mock.patch('analog.renderers.StringIO',
                            side_effect=[TypeError, mock.DEFAULT]
                            ) as mock_stringio:
                csvrenderer.render(report=self.report, path_stats=False)
                assert mock_stringio.call_args_list == [mock.call(newline=''),
                                                        mock.call()]

        # NOTE: returning mock.DEFAULT does not return the default MagicMock
        #       on Python2.7 when using the non-stdlib mock package.
        #       See: https://code.google.com/p/mock/issues/detail?id=190
        except (TypeError, AttributeError) as exc:
            # on Python2.7 it's a TypeError, on PyPy it's an AttributeError
            message = getattr(exc, 'message', getattr(exc, 'args', None))
            if isinstance(message, (list, tuple)):
                message = message[0]
            if message is None or message not in (
                    'argument 1 must have a "write" method',
                    "'_SentinelObject' object has no attribute 'write'"):
                raise
