"""Tests for envdiff.alerting."""

import sys
import pytest

from envdiff.differ import DiffResult
from envdiff.alerting import (
    stdout_alert,
    stderr_alert,
    threshold_alert,
    key_filter_alert,
    multi_alert,
)


@pytest.fixture
def small_result():
    return DiffResult(
        only_in_left={"REMOVED": "old"},
        only_in_right={"ADDED": "new"},
        changed={"CHANGED": ("v1", "v2")},
        unchanged={"SAME": "same"},
    )


@pytest.fixture
def empty_result():
    return DiffResult({}, {}, {}, {"X": "1"})


def test_stdout_alert_prints(small_result, capsys):
    stdout_alert(small_result, label="test event")
    out = capsys.readouterr().out
    assert "test event" in out
    assert "REMOVED" in out or "ADDED" in out or "CHANGED" in out


def test_stderr_alert_prints(small_result, capsys):
    stderr_alert(small_result, label="err event")
    err = capsys.readouterr().err
    assert "err event" in err


def test_threshold_alert_fires_when_met(small_result):
    calls = []
    handler = threshold_alert(lambda r, l: calls.append(r), min_changes=3)
    handler(small_result)
    assert len(calls) == 1


def test_threshold_alert_suppressed_below_threshold(small_result):
    calls = []
    handler = threshold_alert(lambda r, l: calls.append(r), min_changes=10)
    handler(small_result)
    assert calls == []


def test_threshold_alert_empty_result_suppressed(empty_result):
    calls = []
    handler = threshold_alert(lambda r, l: calls.append(r), min_changes=1)
    handler(empty_result)
    assert calls == []


def test_key_filter_alert_fires_on_watched_key(small_result):
    calls = []
    handler = key_filter_alert(lambda r, l: calls.append(r), watched_keys=["CHANGED"])
    handler(small_result)
    assert len(calls) == 1


def test_key_filter_alert_suppressed_when_no_watched_key(small_result):
    calls = []
    handler = key_filter_alert(lambda r, l: calls.append(r), watched_keys=["UNRELATED"])
    handler(small_result)
    assert calls == []


def test_multi_alert_calls_all_handlers(small_result):
    log_a = []
    log_b = []
    handler = multi_alert([
        lambda r, l: log_a.append(r),
        lambda r, l: log_b.append(r),
    ])
    handler(small_result)
    assert len(log_a) == 1
    assert len(log_b) == 1


def test_multi_alert_empty_handlers(small_result):
    handler = multi_alert([])
    handler(small_result)  # should not raise
