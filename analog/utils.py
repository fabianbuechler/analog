"""Utils for the analog module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from collections import Counter
import configparser
import re


class ConfigParser(configparser.ConfigParser):

    """Extension of :py:class:`configparser.ConfigParser` able to parse lists.

    Use ``getlist()`` method to retrieve lists of values separated by comma or
    newline.

    """

    def getlist(self, section, key, fallback=None):
        """Get a list from the config with an optional fallback.

        :param section: section name
        :type section: ``str``
        :param key: key name
        :type key: ``str``
        :param fallback: fallback value if section or key don't exist
        :type fallback: ``list``
        :returns: list from config
        :rtype: ``list``

        """
        try:
            items = re.split(r',|\n', self.get(section, key))
            return list(filter(None, map("".__class__.strip, items)))
        except configparser.Error:
            return fallback


class PrefixMatchingCounter(Counter):

    """Counter-like object that increments a field if it has a common prefix.

    Example: "400", "401", "404" all increment a field named "4".

    """

    def inc(self, field):
        """Increment every field that starts with field by one."""
        for prefix in self.keys():
            if str(field).startswith(str(prefix)):
                self[prefix] += 1
