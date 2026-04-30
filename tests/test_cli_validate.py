"""Tests for envdiff.cli_validate."""

import argparse
from pathlib import Path

import pytest

from envdiff.cli_validate import add_validate_subcommand, run_validate


@pytest.fixture()
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_validate_subcommand(sub)
    return p


@pytest.fixture()
def good_env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("HOST=localhost\nPORT=8080\n")
    return f


@pytest.fixture()
def bad_env_file(tmp_path: Path) -> Path:
    f = tmp_path / "bad.env"
    f.write_text("HOST=\nport=3000\n")  # empty value + lowercase key
    return f


def test_add_validate_subcommand_registers(parser: argparse.ArgumentParser):
    args = parser.parse_args(["validate", "some.env"])
    assert args.files == ["some.env"]


def test_default_rules_are_set(parser: argparse.ArgumentParser):
    args = parser.parse_args(["validate", "some.env"])
    assert "not_empty" in args.rules
    assert "no_spaces_in_key" in args.rules


def test_strict_flag_default_false(parser: argparse.ArgumentParser):
    args = parser.parse_args(["validate", "some.env"])
    assert args.strict is False


def test_strict_flag_can_be_set(parser: argparse.ArgumentParser):
    args = parser.parse_args(["validate", "--strict", "some.env"])
    assert args.strict is True


def test_run_validate_good_file_returns_zero(
    good_env_file: Path, parser: argparse.ArgumentParser
):
    args = parser.parse_args(["validate", str(good_env_file)])
    assert run_validate(args) == 0


def test_run_validate_bad_file_non_strict_returns_zero(
    bad_env_file: Path, parser: argparse.ArgumentParser
):
    args = parser.parse_args(["validate", str(bad_env_file)])
    assert run_validate(args) == 0


def test_run_validate_bad_file_strict_returns_one(
    bad_env_file: Path, parser: argparse.ArgumentParser
):
    args = parser.parse_args(["validate", "--strict", str(bad_env_file)])
    assert run_validate(args) == 1


def test_run_validate_missing_file_returns_two(
    parser: argparse.ArgumentParser,
):
    args = parser.parse_args(["validate", "nonexistent.env"])
    assert run_validate(args) == 2


def test_run_validate_prints_ok_for_valid(good_env_file: Path, parser, capsys):
    args = parser.parse_args(["validate", str(good_env_file)])
    run_validate(args)
    out = capsys.readouterr().out
    assert "[ok]" in out


def test_run_validate_prints_fail_for_invalid(bad_env_file: Path, parser, capsys):
    args = parser.parse_args(["validate", str(bad_env_file)])
    run_validate(args)
    out = capsys.readouterr().out
    assert "[fail]" in out
