"""Utils for the analog module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from collections import Counter


class PrefixMatchingCounter(Counter):

    """
    Counter-like object that increments a field if it has a common prefix.

    Example:
        "400", "401", "404" all increment a field named "4"

    """

    def inc(self, field):
        """Increment every field that starts with field by one."""
        for prefix in self.keys():
            if str(field).startswith(str(prefix)):
                self[prefix] += 1
