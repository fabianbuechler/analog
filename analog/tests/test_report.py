"""Test the analog.report module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from collections import Counter, defaultdict, OrderedDict
import io
import logging

import pytest

from analog.report import ListStats, Report
from analog.utils import PrefixMatchingCounter


@pytest.yield_fixture
def analog_log():
    """Temporarily switch ``analog.LOG`` to a stream handler."""
    stream = io.StringIO()
    log = logging.getLogger('analog')
    log.removeHandler(logging.NullHandler)
    log.addHandler(logging.StreamHandler(stream))
    log.setLevel('DEBUG')
    yield stream
    log.removeHandler(logging.StreamHandler(stream))
    log.addHandler(logging.NullHandler)
    log.setLevel(logging.NOTSET)


def test_liststats():
    """``ListStats`` calculates mean and median of a list of values."""
    values = [1, 2, 3, 4, 5]
    stats = ListStats(values)
    assert stats.mean == 3
    assert stats.median == 3

    values = [1, 1, 1, 1, 6]
    stats = ListStats(values)
    assert stats.mean == 2
    assert stats.median == 1

    # without values no statistics
    stats = ListStats([])
    assert stats.mean is None
    assert stats.median is None


def test_report_initial_data():
    """Initially ``Report`` objects have certain attribute values."""
    report = Report(verbs=['GET', 'POST'], status_codes=['20', 404])

    # execution time still unknown
    assert report.execution_time is None
    # no requests logged
    assert report.requests == 0
    # all verbs prepopulated in Counter, starting with 0
    assert isinstance(report._verbs, Counter)
    assert sorted(report._verbs.keys()) == ['GET', 'POST']
    assert report._verbs['GET'] == 0
    # status codes are using PrefixMatchingCounter, also starting with 0
    assert isinstance(report._status, PrefixMatchingCounter)
    assert sorted(report._status.keys()) == ['20', '404']
    assert report._status['20'] == 0
    # times and bytes to be collected in a list for ListStats evaluation
    assert report._times == []
    assert report._upstream_times == []
    assert report._body_bytes == []
    # requests per path to be recorded in Counter
    assert isinstance(report._path_requests, Counter)
    assert len(report._path_requests.keys()) == 0
    # verbs per path to be recorded in separate Counters
    assert isinstance(report._path_verbs, defaultdict)
    # status codes per path to be recorded in separate Counters
    assert isinstance(report._path_status, defaultdict)
    # times and bytes per path to be collected in separate lists
    assert isinstance(report._path_times, defaultdict)
    assert report._path_times.default_factory is list
    assert isinstance(report._path_upstream_times, defaultdict)
    assert report._path_upstream_times.default_factory is list
    assert isinstance(report._path_body_bytes, defaultdict)
    assert report._path_body_bytes.default_factory is list


def test_report_add():
    """Adding log entries to a report updates all the attribute values."""
    report = Report(verbs=['GET', 'POST'], status_codes=['20', 404])
    report.add(
        path='/foo/bar',
        verb='GET',
        status=205,
        time=0.1,
        upstream_time=0.09,
        body_bytes=255)
    assert report.requests == 1
    assert report._verbs['GET'] == 1
    assert report._status['20'] == 1
    assert report._times == [0.1]
    assert report._upstream_times == [0.09]
    for attribute in ('_path_requests', '_path_verbs', '_path_status',
                      '_path_times', '_path_upstream_times',
                      '_path_body_bytes'):
        assert '/foo/bar' in getattr(report, attribute).keys()
    assert report._path_requests['/foo/bar'] == 1
    assert report._path_verbs['/foo/bar']['GET'] == 1
    assert report._path_status['/foo/bar']['20'] == 1
    assert report._path_times['/foo/bar'] == [0.1]
    assert report._path_upstream_times['/foo/bar'] == [0.09]


def test_report_add_verb_not_tracked(analog_log):
    """Log entries with non-tracked verbs are ignored."""
    report = Report(verbs=['GET', 'POST'], status_codes=['20', 404])
    report.add(
        path='/foo/bar',
        verb='PUT',
        status=205,
        time=0.1,
        upstream_time=0.09,
        body_bytes=255)
    assert report.requests == 0
    out = analog_log.getvalue()
    assert out.startswith("Ignoring log entry for non-tracked")


def test_report_properties():
    """``Report`` objects have statistically evaluated properties."""
    report = Report(verbs=['GET', 'POST'], status_codes=['20', 404])
    report.add(
        path='/foo/bar',
        verb='GET',
        status=205,
        time=0.1,
        upstream_time=0.09,
        body_bytes=255)

    assert report.requests == 1
    # counter attributes evaluate to Counter.most_common()
    assert report.verbs == [('GET', 1), ('POST', 0)]
    assert report.status == [('20', 1), ('404', 0)]
    assert report.path_requests == [('/foo/bar', 1)]
    # list attributes return a ListStats instance
    times = report.times
    assert isinstance(times, ListStats)
    assert times.mean == 0.1
    assert times.median == 0.1
    upstream_times = report.upstream_times
    assert isinstance(upstream_times, ListStats)
    assert upstream_times.mean == 0.09
    assert upstream_times.median == 0.09
    body_bytes = report.body_bytes
    assert isinstance(body_bytes, ListStats)
    assert body_bytes.mean == 255
    assert body_bytes.median == 255
    # per path attributes are ordered dictionaries with path keys
    path_verbs = report.path_verbs
    assert isinstance(path_verbs, OrderedDict)
    assert [key for key in path_verbs.keys()] == ['/foo/bar']
    assert path_verbs['/foo/bar'] == [('GET', 1), ('POST', 0)]
    path_status = report.path_status
    assert isinstance(path_status, OrderedDict)
    assert [key for key in path_status.keys()] == ['/foo/bar']
    assert path_status['/foo/bar'] == [('20', 1), ('404', 0)]
    path_times = report.path_times
    assert isinstance(path_times, OrderedDict)
    assert [key for key in path_times.keys()] == ['/foo/bar']
    assert isinstance(path_times['/foo/bar'], ListStats)
    assert path_times['/foo/bar'].mean == 0.1
    assert path_times['/foo/bar'].median == 0.1
    path_upstream_times = report.path_upstream_times
    assert isinstance(path_upstream_times, OrderedDict)
    assert [key for key in path_upstream_times.keys()] == ['/foo/bar']
    assert isinstance(path_upstream_times['/foo/bar'], ListStats)
    assert path_upstream_times['/foo/bar'].mean == 0.09
    assert path_upstream_times['/foo/bar'].median == 0.09
    path_body_bytes = report.path_body_bytes
    assert isinstance(path_body_bytes, OrderedDict)
    assert [key for key in path_body_bytes.keys()] == ['/foo/bar']
    assert isinstance(path_body_bytes['/foo/bar'], ListStats)
    assert path_body_bytes['/foo/bar'].mean == 255
    assert path_body_bytes['/foo/bar'].median == 255


def test_report_render():
    """``Report.render`` provides a quick method to print reports."""
    report = Report(verbs=['GET', 'POST'], status_codes=['20', 404])
    report.add(
        path='/foo/bar',
        verb='GET',
        status=205,
        time=0.1,
        upstream_time=0.09,
        body_bytes=255)

    output = report.render(path_stats=True, output_format='csv')
    assert output == (
        'path,requests,GET,POST,status_20x,status_404,times_mean,times_median,'
        'upstream_times_mean,upstream_times_median,body_bytes_mean,'
        'body_bytes_median\n'
        '/foo/bar,1,1,0,1,0,0.1,0.1,0.09,0.09,255.0,255\n'
        'total,1,1,0,1,0,0.1,0.1,0.09,0.09,255.0,255')
