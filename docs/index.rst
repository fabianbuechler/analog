.. _index:

=============================
Analog - Log Analysis Utility
=============================

Analog is a weblog analysis utility that provides these metrics:

* Number for requests.
* Response request method (HTTP verb) distribution.
* Response status code distribution.
* Requests per path.
* Response time statistics (mean, median).
* Response upstream time statistics (mean, median).
* Response body size in bytes statistics (mean, median).
* Per path request method (HTTP verb) distribution.
* Per path response status code distribution.
* Per path response time statistics (mean, median).
* Per path response upstream time statistics (mean, median).
* Per path response body size in bytes statistics (mean, median).

Code and issues are on `bitbucket.org/fabianbuechler/analog
<https://bitbucket.org/fabianbuechler/analog>`_. Please also post feature
requests there.

Analog can be installed from PyPI at `pypi.python.org/pypi/analog
<https://pypi.python.org/pypi/analog>`_:

..  code-block:: bash

    $ pip install analog

.. _contents:

Contents
========

.. toctree::
   :maxdepth: 2

   quickstart
   api
   changelog

..  include:: ../AUTHORS

License
-------

..  literalinclude:: ../LICENSE

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
