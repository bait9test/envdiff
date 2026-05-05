"""Tests for envdiff.profiler."""

import pytest
from envdiff.profiler import (
    EnvProfile,
    profile_env,
    compare_profiles,
    _looks_numeric,
    _looks_boolean,
    _looks_url,
)


def test_looks_numeric_integer():
    assert _looks_numeric("42") is True


def test_looks_numeric_float():
    assert _looks_numeric("3.14") is True


def test_looks_numeric_string():
    assert _looks_numeric("hello") is False


def test_looks_boolean_true():
    assert _looks_boolean("true") is True


def test_looks_boolean_yes():
    assert _looks_boolean("yes") is True


def test_looks_boolean_zero():
    assert _looks_boolean("0") is True


def test_looks_boolean_plain_string():
    assert _looks_boolean("maybe") is False


def test_looks_url_https():
    assert _looks_url("https://example.com") is True


def test_looks_url_plain():
    assert _looks_url("example.com") is False


def test_profile_total_keys():
    env = {"A": "1", "B": "hello", "C": ""}
    p = profile_env(env, label="test")
    assert p.total_keys == 3


def test_profile_empty_values():
    env = {"A": "", "B": "value"}
    p = profile_env(env)
    assert "A" in p.empty_values
    assert "B" not in p.empty_values


def test_profile_numeric_values():
    env = {"PORT": "8080", "NAME": "app"}
    p = profile_env(env)
    assert "PORT" in p.numeric_values
    assert "NAME" not in p.numeric_values


def test_profile_boolean_values():
    env = {"DEBUG": "true", "HOST": "localhost"}
    p = profile_env(env)
    assert "DEBUG" in p.boolean_values
    assert "HOST" not in p.boolean_values


def test_profile_url_values():
    env = {"API_URL": "https://api.example.com", "KEY": "abc"}
    p = profile_env(env)
    assert "API_URL" in p.url_values
    assert "KEY" not in p.url_values


def test_profile_longest_key():
    env = {"SHORT": "a", "MUCH_LONGER_KEY": "b"}
    p = profile_env(env)
    assert p.longest_key == "MUCH_LONGER_KEY"


def test_profile_longest_value_key():
    env = {"A": "short", "B": "a much longer value here"}
    p = profile_env(env)
    assert p.longest_value_key == "B"


def test_profile_empty_env():
    p = profile_env({})
    assert p.total_keys == 0
    assert p.longest_key == ""
    assert p.longest_value_key == ""


def test_profile_label():
    p = profile_env({"X": "1"}, label="production")
    assert p.label == "production"


def test_compare_profiles_returns_rows():
    left = profile_env({"A": "1", "B": ""}, label="left")
    right = profile_env({"A": "2", "C": "https://x.com"}, label="right")
    rows = compare_profiles(left, right)
    assert len(rows) == 7
    metrics = [r[0] for r in rows]
    assert "total keys" in metrics
    assert "empty values" in metrics


def test_compare_profiles_values_are_strings():
    left = profile_env({"A": "1"}, label="left")
    right = profile_env({"B": "2"}, label="right")
    rows = compare_profiles(left, right)
    for metric, lv, rv in rows:
        assert isinstance(lv, str)
        assert isinstance(rv, str)
