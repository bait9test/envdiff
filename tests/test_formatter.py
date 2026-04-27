"""Tests for envdiff.formatter module."""

import pytest
from envdiff.differ import diff_envs
from envdiff.formatter import format_diff


LEFT = {"APP_ENV": "production", "DB_HOST": "localhost", "PORT": "8080"}
RIGHT = {"APP_ENV": "staging", "DB_HOST": "localhost", "DEBUG": "true"}


@pytest.fixture
def result():
    return diff_envs(LEFT, RIGHT)


def test_format_shows_only_in_left(result):
    output = format_diff(result, color=False)
    assert "PORT=8080" in output
    assert "Only in [left]" in output


def test_format_shows_only_in_right(result):
    output = format_diff(result, color=False)
    assert "DEBUG=true" in output
    assert "Only in [right]" in output


def test_format_shows_changed(result):
    output = format_diff(result, color=False)
    assert "APP_ENV" in output
    assert "production" in output
    assert "staging" in output


def test_custom_labels(result):
    output = format_diff(result, left_label=".env.prod", right_label=".env.staging", color=False)
    assert ".env.prod" in output
    assert ".env.staging" in output


def test_no_differences_message():
    env = {"A": "1"}
    result = diff_envs(env, env.copy())
    output = format_diff(result, color=False)
    assert "No differences found" in output


def test_show_unchanged(result):
    output = format_diff(result, color=False, show_unchanged=True)
    assert "DB_HOST" in output
    assert "Unchanged keys" in output


def test_hide_unchanged_by_default(result):
    output = format_diff(result, color=False, show_unchanged=False)
    assert "Unchanged keys" not in output


def test_color_codes_present_when_enabled(result):
    output = format_diff(result, color=True)
    assert "\033[" in output


def test_no_color_codes_when_disabled(result):
    output = format_diff(result, color=False)
    assert "\033[" not in output
