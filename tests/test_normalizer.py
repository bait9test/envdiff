"""Tests for envdiff.normalizer."""

import pytest
from envdiff.normalizer import (
    normalize_key,
    normalize_value,
    normalize_env,
    normalize_pair,
)


def test_normalize_key_uppercase():
    assert normalize_key("db_host") == "DB_HOST"


def test_normalize_key_strips_whitespace():
    assert normalize_key("  KEY  ") == "KEY"


def test_normalize_key_no_uppercase():
    assert normalize_key("db_host", uppercase=False) == "db_host"


def test_normalize_key_no_strip():
    assert normalize_key("  KEY  ", strip=False) == "  KEY  "


def test_normalize_value_strips():
    assert normalize_value("  hello  ") == "hello"


def test_normalize_value_no_strip():
    assert normalize_value("  hello  ", strip=False) == "  hello  "


def test_normalize_value_collapse_whitespace():
    assert normalize_value("hello   world", collapse_whitespace=True) == "hello world"


def test_normalize_value_collapse_does_not_affect_stripped():
    assert normalize_value("  a  b  ", collapse_whitespace=True) == "a b"


def test_normalize_env_basic():
    env = {"db_host": "localhost", "PORT": " 5432 "}
    result = normalize_env(env)
    assert result == {"DB_HOST": "localhost", "PORT": "5432"}


def test_normalize_env_collision_last_wins():
    env = {"key": "first", "KEY": "second"}
    result = normalize_env(env)
    assert result["KEY"] == "second"


def test_normalize_env_preserves_all_unique_keys():
    env = {"A": "1", "B": "2", "C": "3"}
    result = normalize_env(env)
    assert set(result.keys()) == {"A", "B", "C"}


def test_normalize_env_collapse_whitespace():
    env = {"MSG": "hello   world"}
    result = normalize_env(env, collapse_whitespace=True)
    assert result["MSG"] == "hello world"


def test_normalize_pair_returns_two_dicts():
    left = {"a": "1"}
    right = {"b": "2"}
    nl, nr = normalize_pair(left, right)
    assert nl == {"A": "1"}
    assert nr == {"B": "2"}


def test_normalize_pair_same_settings_applied():
    left = {"key": " val "}
    right = {"other": " stuff "}
    nl, nr = normalize_pair(left, right)
    assert nl["KEY"] == "val"
    assert nr["OTHER"] == "stuff"
