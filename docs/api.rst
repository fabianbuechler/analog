.. _api:

==========
Analog API
==========

.. _api_main:

``analog`` Command
==================

The primary way to invoke analog is via the ``analog`` command which calls
:py:func:`analog.main.main`.

..  autofunction:: analog.main.main

.. _api_analyzer:

Analyzer
========

The ``Analyzer`` is the main logfile parser class. It uses a
:py:class:`analog.formats.LogFormat` instance to parse the log entries and
passes them on to a :py:class:`analog.report.Report` instance for statistical
analysis. The report itsself can be passed through a
:py:class:`analog.renderers.Renderer` subclass for different report output
formats.

..  autoclass:: analog.analyzer.Analyzer
    :members:
    :special-members:
    :exclude-members: __weakref__

``analyze`` is a convenience wrapper around :py:class:`analog.analyzer.Analyzer`
and can act as the main and only required entry point when using analog from
code.

..  autofunction:: analog.analyzer.analyze

..  autodata:: analog.analyzer.DEFAULT_VERBS
..  autodata:: analog.analyzer.DEFAULT_STATUS_CODES
..  autodata:: analog.analyzer.DEFAULT_PATHS

.. _api_logformat:

Log Format
==========

A ``LogFormat`` defines how log entries are represented in and can be parsed
from a log file.

..  autoclass:: analog.formats.LogFormat
    :members:
    :special-members:
    :exclude-members: __weakref__

Predefined Formats
------------------

``nginx``

    ..  autodata:: analog.formats.NGINX

.. _api_report:

Reports
=======

A ``Report`` collects log entry information and computes the statistical
analysis.

..  autoclass:: analog.report.Report
    :members:
    :special-members:
    :exclude-members: __weakref__

..  autoclass:: analog.report.ListStats
    :members:
    :special-members:
    :exclude-members: __weakref__

.. _api_renderers:

Renderers
=========

Reports are rendered using one of the available renderers. These all implement
the basic :py:class:`analog.renderers.Renderer` interface.

..  autoclass:: analog.renderers.Renderer
    :members:
    :special-members:
    :exclude-members: __weakref__

Available Renderers
-------------------

default

    ..  autoclass:: analog.renderers.PlainTextRenderer

Tabular Data
^^^^^^^^^^^^

..  autoclass:: analog.renderers.TabularDataRenderer
    :members: _tabular_data, _list_stats
    :exclude-members: __weakref__

Visual Tables
"""""""""""""

..  autoclass:: analog.renderers.ASCIITableRenderer

``table``

    ..  autoclass:: analog.renderers.SimpleTableRenderer

``grid``

    ..  autoclass:: analog.renderers.GridTableRenderer

Separated Values
""""""""""""""""

..  autoclass:: analog.renderers.SeparatedValuesRenderer

``csv``

    ..  autoclass:: analog.renderers.CSVRenderer

``tsv``

    ..  autoclass:: analog.renderers.TSVRenderer

.. _api_utils:

Utils
=====

..  autoclass:: analog.utils.AnalogArgumentParser
    :members: convert_arg_line_to_args

..  autoclass:: analog.utils.PrefixMatchingCounter

.. _api_exceptions:

Exceptions
==========

..  automodule:: analog.exceptions
    :members:
