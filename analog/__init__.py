"""Analog - Log Analysis Utitliy."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from analog.analyzer import Analyzer, analyze
from analog.exceptions import MissingArgumentError
from analog.formats import LogFormat
from analog.main import main
from analog.report import Report


__all__ = (
    '__version__',
    Analyzer,
    analyze,
    LogFormat,
    main,
    MissingArgumentError,
    Report,
)


__version__ = None
with open('VERSION') as vfp:
    __version__ = vfp.read().strip()
