"""Tests for envdiff.differ module."""

import pytest
from envdiff.differ import diff_envs, DiffResult


LEFT = {"APP_ENV": "production", "DB_HOST": "localhost", "SECRET": "abc123", "PORT": "8080"}
RIGHT = {"APP_ENV": "staging", "DB_HOST": "localhost", "SECRET": "xyz789", "DEBUG": "true"}


def test_only_in_left():
    result = diff_envs(LEFT, RIGHT)
    assert "PORT" in result.only_in_left
    assert result.only_in_left["PORT"] == "8080"


def test_only_in_right():
    result = diff_envs(LEFT, RIGHT)
    assert "DEBUG" in result.only_in_right
    assert result.only_in_right["DEBUG"] == "true"


def test_changed_values():
    result = diff_envs(LEFT, RIGHT)
    assert "APP_ENV" in result.changed
    assert result.changed["APP_ENV"] == ("production", "staging")
    assert "SECRET" in result.changed


def test_unchanged_values():
    result = diff_envs(LEFT, RIGHT)
    assert "DB_HOST" in result.unchanged
    assert result.unchanged["DB_HOST"] == "localhost"


def test_no_differences():
    env = {"A": "1", "B": "2"}
    result = diff_envs(env, env.copy())
    assert not result.has_differences
    assert len(result.unchanged) == 2


def test_ignore_keys():
    result = diff_envs(LEFT, RIGHT, ignore_keys={"SECRET", "PORT", "DEBUG"})
    assert "SECRET" not in result.changed
    assert "PORT" not in result.only_in_left
    assert "DEBUG" not in result.only_in_right


def test_empty_envs():
    result = diff_envs({}, {})
    assert not result.has_differences


def test_has_differences_flag():
    result = diff_envs(LEFT, RIGHT)
    assert result.has_differences


def test_summary_contains_counts():
    result = diff_envs(LEFT, RIGHT)
    summary = result.summary()
    assert "Only in left" in summary
    assert "Only in right" in summary
    assert "Changed" in summary
