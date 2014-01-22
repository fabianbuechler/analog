"""Analog exceptions."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


class MissingArgumentError(RuntimeError):

    """Error raised when ``Analyzer`` is called without specified format."""


class UnknownRendererError(RuntimeError):

     """Error raised when a renderer is called by name but does not exist. """
