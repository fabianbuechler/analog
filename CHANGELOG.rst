Changelog
=========

0.1.1 - unreleased
------------------

* Strip VERSION when reading it in setup.py.

0.1.0 - 2014-01-26
------------------

* Start documentation: quickstart and CLI usage plus API documentation.

* Add renderers for CSV and TSV output. Use --output [csv|tsv].
  Unified codebase for all tabular renderers.

* Add renderer for tabular output. Use --output [grid|table].

* Also analyze HTTP verbs distribution for overall report.

* Remove timezone aware datetime handling for the moment.

* Introduce Report.add method to not expose Report externals to Analyzer.

* Install pytz on Python <= 3.2 for UTC object. Else use datetime.timezone.

* Add tox environment for py2.7 and py3.3 testing.

* Initial implementation of log analyzer and report object.

* Initial package structure, docs, requirements, test scripts.
