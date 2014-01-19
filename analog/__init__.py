"""Analog - Log Analysis Utitliy."""
from analog.analyzer import Analyzer, analyze
from analog.formats import LogFormat
from analog.main import main
from analog.report import Report


__all__ = (
    '__version__',
    Analyzer,
    analyze,
    LogFormat,
    main,
    Report,
)


__version__ = None
with open('VERSION') as vfp:
    __version__ = vfp.read().strip()
