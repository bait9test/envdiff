"""Tests for envdiff CLI."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from envdiff.cli import build_parser, run


@pytest.fixture()
def env_file_a(tmp_path: Path) -> Path:
    p = tmp_path / ".env.a"
    p.write_text(textwrap.dedent("""\
        SHARED=same
        ONLY_A=hello
        CHANGED=old
    """))
    return p


@pytest.fixture()
def env_file_b(tmp_path: Path) -> Path:
    p = tmp_path / ".env.b"
    p.write_text(textwrap.dedent("""\
        SHARED=same
        ONLY_B=world
        CHANGED=new
    """))
    return p


def test_build_parser_files_subcommand():
    parser = build_parser()
    args = parser.parse_args(["files", "a.env", "b.env"])
    assert args.command == "files"
    assert args.left == "a.env"
    assert args.right == "b.env"


def test_build_parser_no_color_flag():
    parser = build_parser()
    args = parser.parse_args(["files", "a.env", "b.env", "--no-color"])
    assert args.no_color is True


def test_build_parser_custom_labels():
    parser = build_parser()
    args = parser.parse_args(["files", "a.env", "b.env", "--labels", "dev", "prod"])
    assert args.labels == ["dev", "prod"]


def test_build_parser_format_json():
    parser = build_parser()
    args = parser.parse_args(["files", "a.env", "b.env", "--format", "json"])
    assert args.fmt == "json"


def test_build_parser_format_markdown():
    parser = build_parser()
    args = parser.parse_args(["files", "a.env", "b.env", "--format", "markdown"])
    assert args.fmt == "markdown"


def test_run_files_text(env_file_a, env_file_b, capsys):
    rc = run(["files", str(env_file_a), str(env_file_b), "--no-color"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "ONLY_A" in out or "CHANGED" in out


def test_run_files_json(env_file_a, env_file_b, capsys):
    import json
    rc = run(["files", str(env_file_a), str(env_file_b), "--format", "json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "changed" in data
    assert "only_in_left" in data


def test_run_files_markdown(env_file_a, env_file_b, capsys):
    rc = run(["files", str(env_file_a), str(env_file_b), "--format", "markdown"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "# Environment Diff Report" in out


def test_run_missing_file_returns_1(tmp_path):
    rc = run(["files", str(tmp_path / "nope.env"), str(tmp_path / "also_nope.env")])
    assert rc == 1
