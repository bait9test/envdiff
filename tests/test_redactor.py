"""Tests for envdiff.redactor."""

import pytest
from envdiff.redactor import is_sensitive, redact, redact_diff, REDACTED
from envdiff.differ import DiffResult


# ---------------------------------------------------------------------------
# is_sensitive
# ---------------------------------------------------------------------------

def test_is_sensitive_secret():
    assert is_sensitive("MY_SECRET") is True

def test_is_sensitive_password():
    assert is_sensitive("DB_PASSWORD") is True

def test_is_sensitive_token():
    assert is_sensitive("GITHUB_TOKEN") is True

def test_is_sensitive_api_key():
    assert is_sensitive("STRIPE_API_KEY") is True

def test_is_sensitive_plain_key_is_not():
    assert is_sensitive("APP_ENV") is False

def test_is_sensitive_case_insensitive():
    assert is_sensitive("db_password") is True

def test_is_sensitive_custom_pattern():
    assert is_sensitive("MY_PIN", patterns=[r".*PIN.*"]) is True

def test_is_sensitive_custom_pattern_no_match():
    assert is_sensitive("APP_ENV", patterns=[r".*PIN.*"]) is False


# ---------------------------------------------------------------------------
# redact
# ---------------------------------------------------------------------------

def test_redact_replaces_sensitive():
    env = {"DB_PASSWORD": "hunter2", "APP_ENV": "production"}
    result = redact(env)
    assert result["DB_PASSWORD"] == REDACTED
    assert result["APP_ENV"] == "production"

def test_redact_does_not_mutate_original():
    env = {"DB_PASSWORD": "hunter2"}
    redact(env)
    assert env["DB_PASSWORD"] == "hunter2"

def test_redact_custom_placeholder():
    env = {"SECRET_KEY": "abc123"}
    result = redact(env, placeholder="<hidden>")
    assert result["SECRET_KEY"] == "<hidden>"

def test_redact_empty_env():
    assert redact({}) == {}

def test_redact_all_safe_keys_unchanged():
    env = {"HOST": "localhost", "PORT": "5432"}
    assert redact(env) == env


# ---------------------------------------------------------------------------
# redact_diff
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_diff():
    return DiffResult(
        only_in_left={"ONLY_LEFT": "val"},
        only_in_right={"ONLY_RIGHT": "val"},
        changed={
            "DB_PASSWORD": ("old_pass", "new_pass"),
            "APP_ENV": ("staging", "production"),
        },
        unchanged={"HOST": "localhost"},
    )


def test_redact_diff_hides_sensitive_changed(sample_diff):
    result = redact_diff(sample_diff)
    assert result.changed["DB_PASSWORD"] == (REDACTED, REDACTED)

def test_redact_diff_keeps_safe_changed(sample_diff):
    result = redact_diff(sample_diff)
    assert result.changed["APP_ENV"] == ("staging", "production")

def test_redact_diff_preserves_only_in_left(sample_diff):
    result = redact_diff(sample_diff)
    assert result.only_in_left == {"ONLY_LEFT": "val"}

def test_redact_diff_preserves_only_in_right(sample_diff):
    result = redact_diff(sample_diff)
    assert result.only_in_right == {"ONLY_RIGHT": "val"}

def test_redact_diff_preserves_unchanged(sample_diff):
    result = redact_diff(sample_diff)
    assert result.unchanged == {"HOST": "localhost"}
