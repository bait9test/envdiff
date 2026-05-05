"""Tests for envdiff.cli_redact."""

import argparse
import pytest
from unittest.mock import patch, MagicMock

from envdiff.cli_redact import add_redact_subcommand, run_redact
from envdiff.redactor import REDACTED


@pytest.fixture()
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_redact_subcommand(sub)
    return p


def test_add_redact_subcommand_registers(parser):
    args = parser.parse_args(["redact", "some.env"])
    assert args.file == "some.env"


def test_default_placeholder(parser):
    args = parser.parse_args(["redact", "some.env"])
    assert args.placeholder == REDACTED


def test_custom_placeholder(parser):
    args = parser.parse_args(["redact", "some.env", "--placeholder", "<hidden>"])
    assert args.placeholder == "<hidden>"


def test_pattern_flag_appends(parser):
    args = parser.parse_args(["redact", "some.env", "--pattern", r".*PIN.*"])
    assert r".*PIN.*" in args.patterns


def test_show_keys_default_false(parser):
    args = parser.parse_args(["redact", "some.env"])
    assert args.show_keys is False


def test_run_redact_file_not_found(tmp_path, capsys):
    ns = argparse.Namespace(
        file=str(tmp_path / "missing.env"),
        placeholder=REDACTED,
        patterns=None,
        show_keys=False,
    )
    rc = run_redact(ns)
    assert rc == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_run_redact_is_directory(tmp_path, capsys):
    ns = argparse.Namespace(
        file=str(tmp_path),
        placeholder=REDACTED,
        patterns=None,
        show_keys=False,
    )
    rc = run_redact(ns)
    assert rc == 1
    captured = capsys.readouterr()
    assert "directory" in captured.err


def test_run_redact_hides_password(tmp_path, capsys):
    env_file = tmp_path / "test.env"
    env_file.write_text("DB_PASSWORD=secret\nAPP_ENV=production\n")
    ns = argparse.Namespace(
        file=str(env_file),
        placeholder=REDACTED,
        patterns=None,
        show_keys=False,
    )
    rc = run_redact(ns)
    assert rc == 0
    out = capsys.readouterr().out
    assert REDACTED in out
    assert "secret" not in out
    assert "APP_ENV=production" in out


def test_run_redact_show_keys_prints_to_stderr(tmp_path, capsys):
    env_file = tmp_path / "test.env"
    env_file.write_text("GITHUB_TOKEN=abc123\nHOST=localhost\n")
    ns = argparse.Namespace(
        file=str(env_file),
        placeholder=REDACTED,
        patterns=None,
        show_keys=True,
    )
    run_redact(ns)
    err = capsys.readouterr().err
    assert "GITHUB_TOKEN" in err
