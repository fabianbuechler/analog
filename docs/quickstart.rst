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

.. _options:

Options
=======

``analog`` has these options:

``-c`` / ``--config``
    Configuration file for simple definition of request methods (HTTP verbs)
    response status codes and paths to monitor. See :ref:`config` for details.

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

.. _config:

Configuration
=============

The configuration file passed via ``--config`` can be used to define:

*   HTTP *verbs* (request methods) to monitor.

    By default all request methods are monitored. By specifying ``verbs`` you
    can limit to the ones interesting to you.

*   Response *status codes* to monitor (can be grouped).

    By default all separate status codes are monitored. Specify ``status_codes``
    to monitor specific ones. Status can be grouped by defining just the first
    characters. E.g. ``4`` to group all ``4xx`` responses like ``400``, ``401``,
    ``404``, ``409``

*   Request *paths* to monitor (can be grouped).

    By default all exact request paths are monitored. By specifying ``paths``
    these can be limited to a certain set. Also paths are grouped. E.g.
    specifying ``/foo`` would monitor ``/foo/bar`` as well as just ``/foo``.

    Note that paths are evaluated in order of specification. Thus more specific
    paths should be listed first. E.g. ``/foo/bar`` before ``/foo`` would track
    both.

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
