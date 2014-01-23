"""Analog exceptions."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


class AnalogError(RuntimeError):

    """Exception base class for all Analog errors."""


class MissingFormatError(AnalogError):

    """Error raised when ``Analyzer`` is called without format."""


class InvalidFormatExpressionError(AnalogError):

    """Error raised for invalid format regex patterns."""


class UnknownRendererError(AnalogError):

    """Error raised for unknown output format names (to select renderer)."""
