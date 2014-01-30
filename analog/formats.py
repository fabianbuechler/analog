"""Analog log format definitions."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from collections import namedtuple
import re
import weakref

from analog.exceptions import InvalidFormatExpressionError


class LogFormat:

    """Log format definition.

    Represents log format recognition patterns by name.

    A name:format mapping of all defined log format patterns can be retrieved
    using :py:meth:`analog.formats.LogFormat.all_formats`.

    Each log format should at least define the following match groups:

    * ``timestamp``: Local time.
    * ``verb``: HTTP verb (GET, POST, PUT, ...).
    * ``path``: Request path.
    * ``status``: Response status code.
    * ``body_bytes_sent``: Body size in bytes.
    * ``request_time``: Request time.
    * ``upstream_response_time``: Upstream response time.

    """

    #: pool of all predefined log formats
    __formats_ = {}

    #: required pattern groups
    _required_attributes = ('timestamp', 'verb', 'path', 'status',
                            'body_bytes_sent', 'request_time',
                            'upstream_response_time')

    def __init__(self, name, pattern, time_format):
        """Describe log format.

        The format ``pattern`` is a (verbose) regex pattern string specifying
        the log entry attributes as named groups that is compiled into a
        :py:class:`re.Pattern` object.

        All pattern group names are be available as attributes of log entries
        when using a :py:meth:`analog.formats.LogEntry.entry`.

        :param name: log format name.
        :type name: ``str``
        :param pattern: regular expression pattern string.
        :type pattern: raw ``str``
        :param time_format: timestamp parsing pattern.
        :type time_format: ``str``
        :raises: :py:class:`analog.exceptions.InvalidFormatExpressionError` if
            missing required format pattern groups or the pattern is not a valid
            regular expression.

        """
        self.__formats_[name] = weakref.ref(self)
        self.name = name
        try:
            self.pattern = re.compile(pattern, re.UNICODE | re.VERBOSE)
        except re.error:
            raise InvalidFormatExpressionError("Invalid regex in format.")
        attributes = self.pattern.groupindex.keys()
        for attr in self._required_attributes:
            if attr not in attributes:
                raise InvalidFormatExpressionError(
                    "Format pattern must at least define the groups: "
                    "{0}.".format(", ".join(self._required_attributes)))
        self.time_format = time_format
        self._entry = namedtuple(
            'LogEntry{0}'.format(name.title()),
            sorted(self.pattern.groupindex, key=self.pattern.groupindex.get))

    def entry(self, match):
        """Convert regex match object to log entry object.

        :param match: regex match object from ``pattern`` match.
        :type match: :py:class:`re.MatchObject`
        :returns: log entry object with all pattern keys as attributes.
        :rtype: :py:class:`collections.namedtuple`

        """
        return self._entry(**match.groupdict())

    @classmethod
    def all_formats(cls):
        """Mapping of all defined log format patterns.

        :returns: dictionary of name:``LogFormat`` instances.
        :rtype: ``dict``

        """
        formats = {}
        for name, ref in cls.__formats_.items():
            instance = ref()
            if instance is not None:
                formats[name] = instance
        return formats


NGINX = LogFormat('nginx', r'''
    ^(?P<remote_addr>\S+)\s-\s              # Remote address
    (?P<remote_user>\S+)\s                  # Remote user
    \[(?P<timestamp>.*?)\]\s                # Local time
    "                                       # Request
    (?P<verb>[A-Z]+)\s                      # HTTP verb (GET, POST, PUT, ...)
    (?P<path>[^?]+)                         # Request path
    (?:\?.+)?                               # Query string
    \sHTTP/(?:[\d.]+)                       # HTTP/x.x protocol
    "\s                                     # /Request
    (?P<status>\d+?)\s                      # Response status code
    (?P<body_bytes_sent>\d+?)\s             # Body size in bytes
    "(?P<http_referer>[^"]+?)"\s            # Referer header
    "(?P<http_user_agent>[^"]+?)"\s         # User-Agent header
    "(?P<http_x_forwarded_for>[^"]+?)"\s    # X-Forwarded-For header
    (?P<request_time>[\d\.]+)\s             # Request time
    (?P<upstream_response_time>[\d\.]+)\s   # Upstream response time
    (?P<pipe>\S+)?$                         # Pipelined request
    ''', time_format='%d/%b/%Y:%H:%M:%S +0000')
"""Nginx ``combinded_timed`` format::

    '$remote_addr - $remote_user [$time_local] "$request" '
    '$status $body_bytes_sent "$http_referer" '
    '"$http_user_agent" "$http_x_forwarded_for" '
    '$request_time $upstream_response_time $pipe';

"""
