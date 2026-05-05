"""Tests for envdiff.cli_normalize."""

import argparse
import os
import tempfile

import pytest

from envdiff.cli_normalize import add_normalize_subcommand, run_normalize


@pytest.fixture()
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_normalize_subcommand(sub)
    return p


@pytest.fixture()
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("db_host=localhost\nport= 5432 \nAPP_NAME=my app\n")
    return str(f)


def test_add_normalize_subcommand_registers(parser):
    args = parser.parse_args(["normalize", "somefile"])
    assert hasattr(args, "func")


def test_run_normalize_dotenv_output(env_file, capsys):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_normalize_subcommand(sub)
    args = p.parse_args(["normalize", env_file])
    rc = run_normalize(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "DB_HOST=localhost" in out
    assert "PORT=5432" in out


def test_run_normalize_keys_format(env_file, capsys):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_normalize_subcommand(sub)
    args = p.parse_args(["normalize", "--format", "keys", env_file])
    rc = run_normalize(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "DB_HOST" in out
    assert "=" not in out


def test_run_normalize_file_not_found(tmp_path, capsys):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_normalize_subcommand(sub)
    args = p.parse_args(["normalize", str(tmp_path / "missing.env")])
    rc = run_normalize(args)
    assert rc == 1
    assert "not found" in capsys.readouterr().err


def test_run_normalize_is_directory(tmp_path, capsys):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_normalize_subcommand(sub)
    args = p.parse_args(["normalize", str(tmp_path)])
    rc = run_normalize(args)
    assert rc == 1
    assert "directory" in capsys.readouterr().err


def test_run_normalize_no_uppercase(env_file, capsys):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_normalize_subcommand(sub)
    args = p.parse_args(["normalize", "--no-uppercase", env_file])
    rc = run_normalize(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "db_host=localhost" in out


def test_run_normalize_collapse_whitespace(env_file, capsys):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_normalize_subcommand(sub)
    args = p.parse_args(["normalize", "--collapse-whitespace", env_file])
    rc = run_normalize(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "APP_NAME=my app" in out
