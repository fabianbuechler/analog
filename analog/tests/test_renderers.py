"""Test the analog.renderers module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os

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
