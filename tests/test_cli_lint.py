"""Tests for envdiff.cli_lint."""

import argparse
import pytest

from envdiff.cli_lint import add_lint_subcommand, run_lint


@pytest.fixture()
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_lint_subcommand(sub)
    return p


@pytest.fixture()
def clean_env(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DATABASE_URL=postgres://localhost/db\nPORT=5432\n")
    return f


@pytest.fixture()
def dirty_env(tmp_path):
    f = tmp_path / ".env"
    f.write_text("bad_key=value\nEMPTY=\n")
    return f


# ---------------------------------------------------------------------------
# Parser registration
# ---------------------------------------------------------------------------

def test_add_lint_subcommand_registers(parser):
    args = parser.parse_args(["lint", "some.env"])
    assert args.file == "some.env"


def test_default_strict_is_false(parser):
    args = parser.parse_args(["lint", "some.env"])
    assert args.strict is False


def test_strict_flag(parser):
    args = parser.parse_args(["lint", "--strict", "some.env"])
    assert args.strict is True


def test_ignore_flag_single(parser):
    args = parser.parse_args(["lint", "--ignore", "W001", "some.env"])
    assert "W001" in args.ignore


def test_ignore_flag_multiple(parser):
    args = parser.parse_args(["lint", "--ignore", "W001", "--ignore", "E001", "some.env"])
    assert set(args.ignore) == {"W001", "E001"}


# ---------------------------------------------------------------------------
# run_lint exit codes
# ---------------------------------------------------------------------------

def test_clean_file_returns_0(clean_env, capsys):
    args = argparse.Namespace(file=str(clean_env), strict=False, ignore=[])
    code = run_lint(args)
    assert code == 0


def test_clean_file_prints_ok(clean_env, capsys):
    args = argparse.Namespace(file=str(clean_env), strict=False, ignore=[])
    run_lint(args)
    out = capsys.readouterr().out
    assert "OK" in out


def test_dirty_file_returns_1(dirty_env, capsys):
    args = argparse.Namespace(file=str(dirty_env), strict=False, ignore=[])
    code = run_lint(args)
    assert code == 1


def test_dirty_file_prints_issues(dirty_env, capsys):
    args = argparse.Namespace(file=str(dirty_env), strict=False, ignore=[])
    run_lint(args)
    out = capsys.readouterr().out
    assert "E001" in out


def test_warnings_only_strict_returns_1(tmp_path, capsys):
    f = tmp_path / ".env"
    f.write_text("MY_KEY=\n")  # W001 only
    args = argparse.Namespace(file=str(f), strict=True, ignore=[])
    code = run_lint(args)
    assert code == 1


def test_warnings_only_non_strict_returns_0(tmp_path, capsys):
    f = tmp_path / ".env"
    f.write_text("MY_KEY=\n")  # W001 only
    args = argparse.Namespace(file=str(f), strict=False, ignore=[])
    code = run_lint(args)
    assert code == 0


def test_ignore_suppresses_issue(dirty_env, capsys):
    # dirty_env has E001 and W001; ignoring both should give 0
    args = argparse.Namespace(file=str(dirty_env), strict=False, ignore=["E001", "W001"])
    code = run_lint(args)
    assert code == 0


def test_file_not_found_returns_2(tmp_path, capsys):
    args = argparse.Namespace(file="/nonexistent/.env", strict=False, ignore=[])
    code = run_lint(args)
    assert code == 2
    assert "not found" in capsys.readouterr().err
