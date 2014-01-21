"""Analog exceptions."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


class MissingArgumentError(RuntimeError):

    """Error raised when ``Analyzer`` is called without specified format."""
