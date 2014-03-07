"""Test the analog.renderers module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest

from analog import renderers
from analog.exceptions import UnknownRendererError


def test_find_subclasses():
    """``find_subclasses`` looks up subclasses recursively."""
    assert (
        sorted(cls.__name__ for cls in
               renderers.find_subclasses(renderers.Renderer)) ==
        sorted(cls.__name__ for cls in (
            renderers.PlainTextRenderer,
            renderers.TabularDataRenderer,
            renderers.ASCIITableRenderer,
            renderers.SimpleTableRenderer,
            renderers.GridTableRenderer,
            renderers.SeparatedValuesRenderer,
            renderers.CSVRenderer,
            renderers.TSVRenderer)))


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
