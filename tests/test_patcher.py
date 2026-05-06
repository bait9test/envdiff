"""Tests for envdiff.patcher."""

from __future__ import annotations

import pytest

from envdiff.differ import DiffResult, diff_envs
from envdiff.patcher import patch_env, patch_to_dotenv, write_patch


@pytest.fixture()
def base_env():
    return {"A": "1", "B": "2", "C": "3"}


@pytest.fixture()
def diff(base_env):
    right = {"A": "1", "B": "99", "D": "4"}
    return diff_envs(base_env, right)


# --- patch_env ---

def test_patch_applies_changes(base_env, diff):
    result = patch_env(base_env, diff)
    assert result["B"] == "99"


def test_patch_adds_right_only_keys(base_env, diff):
    result = patch_env(base_env, diff)
    assert result["D"] == "4"


def test_patch_keeps_unchanged_keys(base_env, diff):
    result = patch_env(base_env, diff)
    assert result["A"] == "1"


def test_patch_left_only_kept_by_default(base_env, diff):
    result = patch_env(base_env, diff)
    assert "C" in result


def test_patch_removals_removes_left_only(base_env, diff):
    result = patch_env(base_env, diff, apply_removals=True)
    assert "C" not in result


def test_patch_skip_additions(base_env, diff):
    result = patch_env(base_env, diff, apply_additions=False)
    assert "D" not in result


def test_patch_skip_changes(base_env, diff):
    result = patch_env(base_env, diff, apply_changes=False)
    assert result["B"] == "2"


def test_patch_does_not_mutate_base(base_env, diff):
    original = dict(base_env)
    patch_env(base_env, diff)
    assert base_env == original


# --- patch_to_dotenv ---

def test_dotenv_output_sorted():
    env = {"Z": "last", "A": "first"}
    output = patch_to_dotenv(env)
    assert output.index("A=") < output.index("Z=")


def test_dotenv_quotes_values_with_spaces():
    env = {"MSG": "hello world"}
    output = patch_to_dotenv(env)
    assert 'MSG="hello world"' in output


def test_dotenv_no_quotes_plain_value():
    env = {"KEY": "value"}
    output = patch_to_dotenv(env)
    assert "KEY=value" in output


def test_dotenv_ends_with_newline():
    env = {"X": "1"}
    assert patch_to_dotenv(env).endswith("\n")


def test_dotenv_empty_env_is_empty_string():
    assert patch_to_dotenv({}) == ""


# --- write_patch ---

def test_write_patch_creates_file(tmp_path, base_env, diff):
    out = tmp_path / "patched.env"
    write_patch(base_env, diff, str(out))
    assert out.exists()


def test_write_patch_content_has_changed_value(tmp_path, base_env, diff):
    out = tmp_path / "patched.env"
    write_patch(base_env, diff, str(out))
    content = out.read_text()
    assert "B=99" in content


def test_write_patch_respects_apply_removals(tmp_path, base_env, diff):
    out = tmp_path / "patched.env"
    write_patch(base_env, diff, str(out), apply_removals=True)
    content = out.read_text()
    assert "C=" not in content
