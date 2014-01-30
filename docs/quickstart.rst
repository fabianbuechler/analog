.. _quickstart:

==========
Quickstart
==========

Use the ``analog`` CLI to start the analysis:

..  code-block:: bash

    $ analog --format nginx /var/log/nginx/mysite.access.log

This invokes the analyzer with a predefined Nginx log format and will by default
parse the complete logfile for all different request paths and analyze all
different request methods (e.g. ``GET``, ``PUT``) and response status codes
(e.g. ``200``, ``401``, ``404``, ``409``, ``500``). The report would be printed
to standard out as a simple list. Use normal piping to save the report output in
a file.

For details on the ``analog`` command see :py:func:`analog.main.main`

.. _options:

Options
=======

``analog`` has these options:

``-f`` / ``--format``
    Log format identifier. Currently only ``nginx`` is predefined. Alternatively
    a regular expression pattern can be defined manually using ``--regex``.

``-r`` / ``--regex``
    Regular expression log format pattern. Define named groups for all
    attributes to match. Required attributes are: ``timestamp``, ``verb``,
    ``path``, ``status``, ``body_bytes_sent``, ``request_time``,
    ``upstream_response_time``. See :ref:`log formats <api_logformat>` for
    details.

``-o`` / ``--output``
    Output format. Defaults to plaintext list output. Choose from ``table``,
    ``grid``, ``csv`` and ``tsv`` for tabuular formats. For details see
    :ref:`the available report renderers <api_renderers>`

``-p`` / ``--path``
    Path(s) to monitor. If not provided, all distinct paths will be analyzed.
    Groups paths by matching the beginng of the log entry values.

``-v`` / ``--verb``
    HTTP verbs(s) to monitor. If not provided, by default ``DELETE``, ``GET``,
    ``PATCH``, ``POST`` and ``PUT`` will be analyzed.

``-s`` / ``--status``
    Response status codes(s) to monitor. If not provided, by default ``1``,
    ``2``, ``3``, ``4`` and ``5`` are analyzed.
    Groups paths by matching the beginng of the log entry values.

``-a`` / ``--max-age``
    Limit the maximum age of log entries to analyze in minutes. Useful for
    continuous analysis of the same logfile (e.g. the last ten minutes every ten
    minutes).

``-ps`` / ``--path-stats``
    Include per-path statistics in the analysis report output. By default analog
    only generates overall statistics.

``-t`` / ``--timing``
    Tracks and prints analysis time.

``-v`` / ``--version``
    Print analog version and exit.

``-h`` / ``--help``
    Print manual and exit.


.. _options_file:

Options from File
-----------------

To specify the options via a file, call ``analog`` like this:

..  code-block:: bash

    $ analog @arguments.txt logfile.log

The ``arguments.txt`` (can have any name) contains one argument per line.
Arguments and their values can also be comma- or whitespace-separated on one
line. For example::

    --format=nginx
    -o       table
    --verb   GET, POST, PUT
    --verb   PATCH
    --status 404, 500
    --path   /foo/bar
    --path   /baz
    --path-stats
    -t
    some_logfile.log

See :py:class:`analog.utils.AnalogArgumentParser` for details.

Example
-------

..  code-block:: ini

    [analog]
    verbs = DELETE, GET, PATCH, POST, PUT
    status_codes = 1, 2, 3, 4, 5, 404, 500
    paths =
        /docs/api
        /docs
        /index.html
        /some/path/group
