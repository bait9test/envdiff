"""Tests for envdiff.filter module."""

import pytest
from envdiff.filter import (
    apply_filters,
    exclude_keys,
    filter_by_pattern,
    filter_by_prefix,
    filter_by_regex,
)

SAMPLE: dict = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_ENV": "production",
    "APP_DEBUG": "false",
    "SECRET_KEY": "abc123",
    "LOG_LEVEL": "info",
}


def test_filter_by_prefix_single():
    result = filter_by_prefix(SAMPLE, ["DB_"])
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_by_prefix_multiple():
    result = filter_by_prefix(SAMPLE, ["DB_", "APP_"])
    assert set(result.keys()) == {"DB_HOST", "DB_PORT", "APP_ENV", "APP_DEBUG"}


def test_filter_by_prefix_empty_returns_all():
    result = filter_by_prefix(SAMPLE, [])
    assert result == SAMPLE


def test_filter_by_prefix_no_match():
    result = filter_by_prefix(SAMPLE, ["REDIS_"])
    assert result == {}


def test_filter_by_pattern_wildcard():
    result = filter_by_pattern(SAMPLE, "DB_*")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_by_pattern_exact():
    result = filter_by_pattern(SAMPLE, "LOG_LEVEL")
    assert result == {"LOG_LEVEL": "info"}


def test_filter_by_pattern_no_match():
    result = filter_by_pattern(SAMPLE, "NOPE_*")
    assert result == {}


def test_filter_by_regex_simple():
    result = filter_by_regex(SAMPLE, r"^DB_")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_by_regex_contains():
    result = filter_by_regex(SAMPLE, r"_KEY$")
    assert set(result.keys()) == {"SECRET_KEY"}


def test_filter_by_regex_invalid_raises():
    import re
    with pytest.raises(re.error):
        filter_by_regex(SAMPLE, r"[invalid")


def test_exclude_keys_removes_listed():
    result = exclude_keys(SAMPLE, ["SECRET_KEY", "LOG_LEVEL"])
    assert "SECRET_KEY" not in result
    assert "LOG_LEVEL" not in result
    assert len(result) == len(SAMPLE) - 2


def test_exclude_keys_empty_list():
    result = exclude_keys(SAMPLE, [])
    assert result == SAMPLE


def test_apply_filters_prefix_and_exclude():
    result = apply_filters(SAMPLE, prefixes=["DB_"], exclude=["DB_PORT"])
    assert result == {"DB_HOST": "localhost"}


def test_apply_filters_pattern_and_regex():
    result = apply_filters(SAMPLE, pattern="APP_*", regex=r"DEBUG")
    assert result == {"APP_DEBUG": "false"}


def test_apply_filters_no_filters_returns_copy():
    result = apply_filters(SAMPLE)
    assert result == SAMPLE
    assert result is not SAMPLE
