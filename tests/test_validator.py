"""Tests for envdiff.validator."""

import pytest

from envdiff.validator import (
    ValidationError,
    ValidationResult,
    rule_key_uppercase,
    rule_matches_pattern,
    rule_no_spaces_in_key,
    rule_not_empty,
    validate_env,
)


# --- unit tests for individual rules ---

def test_rule_not_empty_passes():
    assert rule_not_empty("KEY", "value") is None


def test_rule_not_empty_fails_on_blank():
    assert rule_not_empty("KEY", "") is not None
    assert rule_not_empty("KEY", "   ") is not None


def test_rule_no_spaces_in_key_passes():
    assert rule_no_spaces_in_key("MY_KEY", "val") is None


def test_rule_no_spaces_in_key_fails():
    msg = rule_no_spaces_in_key("MY KEY", "val")
    assert msg is not None
    assert "spaces" in msg


def test_rule_key_uppercase_passes():
    assert rule_key_uppercase("MY_KEY", "val") is None


def test_rule_key_uppercase_fails():
    msg = rule_key_uppercase("my_key", "val")
    assert msg is not None
    assert "uppercase" in msg


def test_rule_matches_pattern_passes():
    rule = rule_matches_pattern(r"\d+")
    assert rule("PORT", "8080") is None


def test_rule_matches_pattern_fails():
    rule = rule_matches_pattern(r"\d+")
    msg = rule("PORT", "abc")
    assert msg is not None
    assert "pattern" in msg


# --- validate_env integration tests ---

def test_validate_env_all_valid():
    env = {"HOST": "localhost", "PORT": "8080"}
    result = validate_env(env)
    assert result.valid
    assert len(result) == 0


def test_validate_env_empty_value_raises_error():
    env = {"HOST": ""}
    result = validate_env(env)
    assert not result.valid
    assert any(e.key == "HOST" for e in result.errors)


def test_validate_env_key_with_space_raises_error():
    env = {"MY KEY": "value"}
    result = validate_env(env)
    assert not result.valid


def test_validate_env_custom_rules():
    env = {"port": "8080"}
    result = validate_env(env, rules=[rule_key_uppercase])
    assert not result.valid
    assert result.errors[0].key == "port"


def test_validate_env_multiple_errors():
    env = {"bad key": "", "GOOD": "ok"}
    result = validate_env(env)
    error_keys = [e.key for e in result.errors]
    assert "bad key" in error_keys


def test_validation_error_str():
    err = ValidationError(key="FOO", message="something wrong")
    assert "FOO" in str(err)
    assert "something wrong" in str(err)


def test_validate_env_no_rules_returns_valid():
    env = {"any key": ""}
    result = validate_env(env, rules=[])
    assert result.valid
