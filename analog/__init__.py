"""Analog - Log Analysis Utitliy."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os

import analog
from analog.analyzer import Analyzer, analyze
from analog.exceptions import (AnalogError, InvalidFormatExpressionError,
                               MissingFormatError, UnknownRendererError)
from analog.formats import LogFormat
from analog.main import main
from analog.report import Report
from analog.renderers import Renderer


__all__ = (
    '__version__',
    AnalogError,
    analyze,
    Analyzer,
    InvalidFormatExpressionError,
    LogFormat,
    main,
    MissingFormatError,
    Renderer,
    Report,
    UnknownRendererError,
)


__version__ = None
with open(os.path.abspath(
        os.path.join(os.path.dirname(analog.__file__),
                     os.path.pardir, 'VERSION'))) as vfp:
    __version__ = vfp.read().strip()
