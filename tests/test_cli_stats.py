"""Tests for envdiff.cli_stats."""
from __future__ import annotations

import argparse
import json
import os
import textwrap

import pytest

from envdiff.cli_stats import add_stats_subcommand, run_stats


@pytest.fixture()
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_stats_subcommand(sub)
    return p


@pytest.fixture()
def env_file_a(tmp_path):
    f = tmp_path / ".env.a"
    f.write_text(textwrap.dedent("""\
        FOO=bar
        BAZ=qux
        COMMON=same
    """))
    return str(f)


@pytest.fixture()
def env_file_b(tmp_path):
    f = tmp_path / ".env.b"
    f.write_text(textwrap.dedent("""\
        FOO=changed
        EXTRA=only_right
        COMMON=same
    """))
    return str(f)


def test_add_stats_subcommand_registers(parser):
    args = parser.parse_args(["stats", "a.env", "b.env"])
    assert args.func is run_stats


def test_default_format_is_text(parser):
    args = parser.parse_args(["stats", "a.env", "b.env"])
    assert args.fmt == "text"


def test_run_stats_text_output(env_file_a, env_file_b, capsys):
    args = argparse.Namespace(
        left=env_file_a, right=env_file_b, fmt="text", no_color=True
    )
    rc = run_stats(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "Total keys" in out
    assert "Change rate" in out


def test_run_stats_json_output(env_file_a, env_file_b, capsys):
    args = argparse.Namespace(
        left=env_file_a, right=env_file_b, fmt="json", no_color=True
    )
    rc = run_stats(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "total_keys" in data
    assert "change_rate" in data


def test_run_stats_missing_file_returns_1(env_file_a, capsys):
    args = argparse.Namespace(
        left=env_file_a, right="/no/such/file.env", fmt="text", no_color=True
    )
    rc = run_stats(args)
    assert rc == 1
    assert "error" in capsys.readouterr().err


def test_run_stats_json_values_correct(env_file_a, env_file_b, capsys):
    args = argparse.Namespace(
        left=env_file_a, right=env_file_b, fmt="json", no_color=True
    )
    run_stats(args)
    data = json.loads(capsys.readouterr().out)
    # FOO changed, BAZ only_left, EXTRA only_right, COMMON unchanged
    assert data["changed"] == 1
    assert data["only_in_left"] == 1
    assert data["only_in_right"] == 1
    assert data["unchanged"] == 1
