"""Tests for envdiff.cli_tag."""

import argparse
import json
from pathlib import Path

import pytest

from envdiff.cli_tag import add_tag_subcommand, run_tag


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_tag_subcommand(sub)
    return p


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text(
        "AWS_ACCESS_KEY_ID=AKIA123\n"
        "AWS_SECRET=topsecret\n"
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "APP_URL=http://example.com\n"
    )
    return f


def test_add_tag_subcommand_registers(parser):
    args = parser.parse_args(["tag", "/dev/null"])
    assert args.command == "tag"


def test_run_tag_no_rules_returns_error(env_file, capsys):
    args = argparse.Namespace(
        file=str(env_file), prefixes=[], patterns=[], fmt="text"
    )
    rc = run_tag(args)
    assert rc == 1
    captured = capsys.readouterr()
    assert "No --prefix" in captured.err


def test_run_tag_prefix_text_output(env_file, capsys):
    args = argparse.Namespace(
        file=str(env_file),
        prefixes=[["AWS_", "aws"]],
        patterns=[],
        fmt="text",
    )
    rc = run_tag(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "[aws]" in out
    assert "AWS_ACCESS_KEY_ID" in out


def test_run_tag_prefix_json_output(env_file, capsys):
    args = argparse.Namespace(
        file=str(env_file),
        prefixes=[["DB_", "database"]],
        patterns=[],
        fmt="json",
    )
    rc = run_tag(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "database" in data
    assert "DB_HOST" in data["database"]


def test_run_tag_pattern_output(env_file, capsys):
    args = argparse.Namespace(
        file=str(env_file),
        prefixes=[],
        patterns=[["*URL*", "network"]],
        fmt="text",
    )
    rc = run_tag(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "[network]" in out
    assert "APP_URL" in out


def test_run_tag_combined_prefix_and_pattern(env_file, capsys):
    args = argparse.Namespace(
        file=str(env_file),
        prefixes=[["DB_", "infra"]],
        patterns=[["*URL*", "infra"]],
        fmt="json",
    )
    rc = run_tag(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "infra" in data
    assert "DB_HOST" in data["infra"]
    assert "APP_URL" in data["infra"]
