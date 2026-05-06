"""Tests for envdiff.watcher."""

import os
import time
import pytest

from envdiff.watcher import watch_file, watch_two_files


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("FOO=bar\nBAZ=qux\n")
    return p


@pytest.fixture
def env_file_b(tmp_path):
    p = tmp_path / ".env.b"
    p.write_text("FOO=bar\n")
    return p


def test_watch_file_no_change_no_callback(env_file):
    calls = []
    watch_file(str(env_file), calls.append, interval=0.05, max_cycles=3)
    assert calls == []


def test_watch_file_detects_change(env_file):
    calls = []

    def modify_after_first(result):
        calls.append(result)

    # Write a change after a short delay using a side-effect approach
    original = str(env_file)

    results = []

    def callback(r):
        results.append(r)

    # Modify the file before the watcher's first poll
    time.sleep(0.01)
    env_file.write_text("FOO=changed\nBAZ=qux\n")
    # Bump mtime explicitly to ensure detection
    now = time.time() + 1
    os.utime(str(env_file), (now, now))

    watch_file(original, callback, interval=0.05, max_cycles=2)
    assert len(results) == 1
    assert "FOO" in results[0].changed


def test_watch_file_missing_file(tmp_path):
    missing = str(tmp_path / "nonexistent.env")
    calls = []
    # Should not raise even if file doesn't exist
    watch_file(missing, calls.append, interval=0.05, max_cycles=2)
    assert calls == []


def test_watch_two_files_no_change(env_file, env_file_b):
    calls = []
    watch_two_files(str(env_file), str(env_file_b), calls.append, interval=0.05, max_cycles=3)
    assert calls == []


def test_watch_two_files_detects_change(env_file, env_file_b):
    results = []

    now = time.time() + 2
    env_file_b.write_text("FOO=bar\nNEW=value\n")
    os.utime(str(env_file_b), (now, now))

    watch_two_files(str(env_file), str(env_file_b), results.append, interval=0.05, max_cycles=2)
    assert len(results) == 1
    assert "NEW" in results[0].only_in_right


def test_watch_two_files_both_missing(tmp_path):
    calls = []
    a = str(tmp_path / "a.env")
    b = str(tmp_path / "b.env")
    watch_two_files(a, b, calls.append, interval=0.05, max_cycles=2)
    assert calls == []


def test_watch_two_files_only_one_missing(env_file, tmp_path):
    """Watcher should not crash or fire callbacks when one of the two files is missing."""
    calls = []
    missing = str(tmp_path / "missing.env")
    watch_two_files(str(env_file), missing, calls.append, interval=0.05, max_cycles=2)
    assert calls == []
