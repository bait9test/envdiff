"""Tests for envdiff.cli_template."""

import argparse
import sys

import pytest

from envdiff.cli_template import add_template_subcommand, run_template


@pytest.fixture()
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_template_subcommand(sub)
    return p


@pytest.fixture()
def env_file_a(tmp_path):
    f = tmp_path / "a.env"
    f.write_text("APP=myapp\nDEBUG=true\nSHARED=hello\n")
    return str(f)


@pytest.fixture()
def env_file_b(tmp_path):
    f = tmp_path / "b.env"
    f.write_text("SHARED=world\nNEW_KEY=123\n")
    return str(f)


def test_add_template_subcommand_registers(parser):
    args = parser.parse_args(["template", "some.env"])
    assert hasattr(args, "func")


def test_default_placeholder(parser):
    args = parser.parse_args(["template", "a.env"])
    assert args.placeholder == "<FILL_ME>"


def test_custom_placeholder(parser):
    args = parser.parse_args(["template", "--placeholder", "TODO", "a.env"])
    assert args.placeholder == "TODO"


def test_include_values_flag(parser):
    args = parser.parse_args(["template", "--include-values", "a.env"])
    assert args.include_values is True


def test_no_comments_flag(parser):
    args = parser.parse_args(["template", "--no-comments", "a.env"])
    assert args.no_comments is True


def test_run_template_single_file_stdout(env_file_a, capsys):
    args = argparse.Namespace(
        files=[env_file_a],
        placeholder="<FILL_ME>",
        include_values=False,
        no_comments=False,
        output=None,
    )
    rc = run_template(args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "APP=<FILL_ME>" in out
    assert "DEBUG=<FILL_ME>" in out


def test_run_template_two_files_stdout(env_file_a, env_file_b, capsys):
    args = argparse.Namespace(
        files=[env_file_a, env_file_b],
        placeholder="<FILL_ME>",
        include_values=False,
        no_comments=False,
        output=None,
    )
    rc = run_template(args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "SHARED=" in out
    assert "APP=" in out
    assert "NEW_KEY=" in out


def test_run_template_writes_to_output_file(env_file_a, tmp_path):
    dest = str(tmp_path / "out.env")
    args = argparse.Namespace(
        files=[env_file_a],
        placeholder="<FILL_ME>",
        include_values=False,
        no_comments=False,
        output=dest,
    )
    rc = run_template(args)
    assert rc == 0
    content = open(dest).read()
    assert "APP=<FILL_ME>" in content


def test_run_template_too_many_files_returns_error(capsys):
    args = argparse.Namespace(
        files=["a.env", "b.env", "c.env"],
        placeholder="<FILL_ME>",
        include_values=False,
        no_comments=False,
        output=None,
    )
    rc = run_template(args)
    assert rc == 1
