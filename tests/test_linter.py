"""Tests for envdiff.linter."""

import pytest

from envdiff.linter import LintIssue, LintResult, lint_env, lint_file, _build_line_map


# ---------------------------------------------------------------------------
# LintResult helpers
# ---------------------------------------------------------------------------

def test_lint_result_ok_when_no_issues():
    assert LintResult().ok is True


def test_lint_result_not_ok_when_issues():
    r = LintResult(issues=[LintIssue(1, "foo", "E001", "msg")])
    assert r.ok is False


def test_lint_result_len():
    r = LintResult(issues=[LintIssue(0, "a", "E001", "x"), LintIssue(0, "b", "W001", "y")])
    assert len(r) == 2


def test_lint_result_by_code():
    r = LintResult(issues=[
        LintIssue(0, "a", "E001", "x"),
        LintIssue(0, "b", "W001", "y"),
        LintIssue(0, "c", "E001", "z"),
    ])
    assert len(r.by_code("E001")) == 2
    assert len(r.by_code("W001")) == 1
    assert len(r.by_code("E999")) == 0


def test_lint_issue_str():
    issue = LintIssue(3, "my_key", "E001", "Key should be uppercase")
    s = str(issue)
    assert "Line 3" in s
    assert "E001" in s
    assert "my_key" in s


# ---------------------------------------------------------------------------
# lint_env checks
# ---------------------------------------------------------------------------

def test_no_issues_for_clean_env():
    env = {"DATABASE_URL": "postgres://localhost/db", "PORT": "5432"}
    result = lint_env(env)
    assert result.ok


def test_e001_lowercase_key():
    result = lint_env({"database_url": "value"})
    codes = [i.code for i in result.issues]
    assert "E001" in codes


def test_e002_key_with_leading_whitespace():
    result = lint_env({" KEY": "value"})
    codes = [i.code for i in result.issues]
    assert "E002" in codes


def test_e003_key_with_spaces():
    result = lint_env({"MY KEY": "value"})
    codes = [i.code for i in result.issues]
    assert "E003" in codes


def test_w001_empty_value():
    result = lint_env({"MY_KEY": ""})
    codes = [i.code for i in result.issues]
    assert "W001" in codes


def test_w002_value_with_trailing_space():
    result = lint_env({"MY_KEY": "value "})
    codes = [i.code for i in result.issues]
    assert "W002" in codes


def test_w003_very_long_value():
    result = lint_env({"MY_KEY": "x" * 513})
    codes = [i.code for i in result.issues]
    assert "W003" in codes


def test_multiple_issues_same_key():
    result = lint_env({"bad key": ""})
    codes = [i.code for i in result.issues]
    assert "E001" in codes
    assert "E003" in codes
    assert "W001" in codes


# ---------------------------------------------------------------------------
# _build_line_map
# ---------------------------------------------------------------------------

def test_build_line_map_basic():
    lines = ["# comment\n", "FOO=bar\n", "BAZ=qux\n"]
    m = _build_line_map(lines)
    assert m["FOO"] == 2
    assert m["BAZ"] == 3


def test_build_line_map_skips_comments():
    lines = ["# FOO=ignored\n", "FOO=real\n"]
    m = _build_line_map(lines)
    assert m["FOO"] == 2


# ---------------------------------------------------------------------------
# lint_file integration
# ---------------------------------------------------------------------------

def test_lint_file_clean(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DATABASE_URL=postgres://localhost/db\nPORT=5432\n")
    result = lint_file(str(f))
    assert result.ok


def test_lint_file_detects_issues(tmp_path):
    f = tmp_path / ".env"
    f.write_text("database_url=postgres://localhost/db\nEMPTY=\n")
    result = lint_file(str(f))
    assert not result.ok
    codes = [i.code for i in result.issues]
    assert "E001" in codes
    assert "W001" in codes


def test_lint_file_line_numbers(tmp_path):
    f = tmp_path / ".env"
    f.write_text("GOOD=ok\nbad_key=value\n")
    result = lint_file(str(f))
    e001 = result.by_code("E001")
    assert len(e001) == 1
    assert e001[0].line == 2
