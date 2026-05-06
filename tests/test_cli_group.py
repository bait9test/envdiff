"""Tests for envdiff.cli_group."""

import argparse
import json
from pathlib import Path

import pytest

from envdiff.cli_group import add_group_subcommand, run_group, _parse_rules


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_group_subcommand(sub)
    return p


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "DB_NAME=mydb\n"
        "AWS_KEY=AKIA\n"
        "AWS_SECRET=secret\n"
        "DEBUG=true\n"
    )
    return str(f)


# --- add_group_subcommand ---

def test_add_group_subcommand_registers(parser):
    args = parser.parse_args(["group", "some.env"])
    assert hasattr(args, "func")


def test_default_sep_is_underscore(parser):
    args = parser.parse_args(["group", "some.env"])
    assert args.sep == "_"


def test_default_format_is_text(parser):
    args = parser.parse_args(["group", "some.env"])
    assert args.fmt == "text"


def test_default_min_size_is_one(parser):
    args = parser.parse_args(["group", "some.env"])
    assert args.min_size == 1


# --- _parse_rules ---

def test_parse_rules_basic():
    result = _parse_rules(["Database:DB_", "Cloud:AWS_"])
    assert result == {"Database": ["DB_"], "Cloud": ["AWS_"]}


def test_parse_rules_same_group_multiple_prefixes():
    result = _parse_rules(["Infra:DB_", "Infra:REDIS_"])
    assert result["Infra"] == ["DB_", "REDIS_"]


def test_parse_rules_malformed_skipped(capsys):
    result = _parse_rules(["BADENTRY"])
    assert result == {}
    captured = capsys.readouterr()
    assert "malformed" in captured.err


def test_parse_rules_none_returns_empty():
    assert _parse_rules(None) == {}


# --- run_group text output ---

def test_run_group_text_shows_group_names(parser, env_file, capsys):
    args = parser.parse_args(["group", env_file])
    rc = run_group(args)
    captured = capsys.readouterr()
    assert rc == 0
    assert "[DB]" in captured.out
    assert "[AWS]" in captured.out


def test_run_group_text_shows_keys(parser, env_file, capsys):
    args = parser.parse_args(["group", env_file])
    run_group(args)
    captured = capsys.readouterr()
    assert "DB_HOST" in captured.out
    assert "AWS_SECRET" in captured.out


def test_run_group_json_output(parser, env_file, capsys):
    args = parser.parse_args(["group", env_file, "--format", "json"])
    rc = run_group(args)
    captured = capsys.readouterr()
    assert rc == 0
    data = json.loads(captured.out)
    assert "DB" in data
    assert data["DB"]["count"] == 3


def test_run_group_custom_rules(parser, env_file, capsys):
    args = parser.parse_args(
        ["group", env_file, "--rule", "Database:DB_", "--rule", "Cloud:AWS_"]
    )
    run_group(args)
    captured = capsys.readouterr()
    assert "[Database]" in captured.out
    assert "[Cloud]" in captured.out


def test_run_group_missing_file_returns_1(parser, tmp_path, capsys):
    args = parser.parse_args(["group", str(tmp_path / "missing.env")])
    rc = run_group(args)
    assert rc == 1
    assert "not found" in capsys.readouterr().err


def test_run_group_min_size_folds_small_groups(parser, env_file, capsys):
    # AWS has 2 keys; DEBUG has 1 — with min_size=3 only DB survives as own group
    args = parser.parse_args(["group", env_file, "--min-size", "3"])
    run_group(args)
    captured = capsys.readouterr()
    assert "[DB]" in captured.out
    assert "[AWS]" not in captured.out
