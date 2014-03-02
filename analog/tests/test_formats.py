"""Test the analog.formats module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime

import pytest

from analog.exceptions import InvalidFormatExpressionError
from analog.formats import LogFormat, NGINX


def test_predefined_valid_nginx():
    """The predefined ``NGINX`` ``LogFormat`` is valid."""
    # NGINX is a LogFormat instance and registered as such
    assert isinstance(NGINX, LogFormat)
    assert 'nginx' in LogFormat.all_formats()
    # all required match groups are available
    match_groups = NGINX.pattern.groupindex.keys()
    for required in LogFormat._required_attributes:
        assert required in match_groups
    # timestamp conversion is working
    now = datetime.datetime.now().replace(microsecond=0)
    now_str = now.strftime(NGINX.time_format)
    now_parsed = datetime.datetime.strptime(now_str, NGINX.time_format)
    assert now == now_parsed
    # try matching a log entry
    log_line = ('123.123.123.123 - test_client [16/Jan/2014:13:30:30 +0000] '
                '"POST /auth/token HTTP/1.1" 200 174 "-" '
                '"OAuthClient 0.2.3" "-" 0.633 0.633')
    match = NGINX.pattern.search(log_line)
    log_entry = NGINX.entry(match)
    # all entry attributes are correctly populated
    assert log_entry.remote_addr == '123.123.123.123'
    assert log_entry.remote_user == 'test_client'
    assert log_entry.timestamp == '16/Jan/2014:13:30:30 +0000'
    assert log_entry.verb == 'POST'
    assert log_entry.path == '/auth/token'
    assert log_entry.status == '200'
    assert log_entry.body_bytes_sent == '174'
    assert log_entry.http_referer == '-'
    assert log_entry.http_user_agent == 'OAuthClient 0.2.3'
    assert log_entry.http_x_forwarded_for == '-'
    assert log_entry.request_time == '0.633'
    assert log_entry.upstream_response_time == '0.633'


def test_custom_logformat_missing_groups():
    """Custom ``LogFormat`` patterns must include all required match groups."""
    pattern_regex = r'(?P<some_group>.*)'
    time_format = '%d/%b/%Y:%H:%M:%S +0000'
    with pytest.raises(InvalidFormatExpressionError) as exc:
        LogFormat('invalid', pattern_regex, time_format)
    assert ('InvalidFormatExpressionError: '
            'Format pattern must at least define the groups: {0}'.format(
                ', '.join(LogFormat._required_attributes))) in str(exc)


def test_custom_logformat_invalid_regex():
    """Custom ``LogFormat`` patterns must be valid regular expressions."""
    pattern_regex = r'(?P<incomplete)'
    time_format = '%d/%b/%Y:%H:%M:%S +0000'
    with pytest.raises(InvalidFormatExpressionError) as exc:
        LogFormat('invalid', pattern_regex, time_format)
    assert 'Invalid regex in format.' in str(exc)
