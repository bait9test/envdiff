"""Tests for the CLI module."""

import os
import pytest
from unittest.mock import patch, MagicMock

from envdiff.cli import build_parser, run


@pytest.fixture
def env_file_a(tmp_path):
    f = tmp_path / ".env.a"
    f.write_text("FOO=bar\nBAZ=qux\n")
    return str(f)


@pytest.fixture
def env_file_b(tmp_path):
    f = tmp_path / ".env.b"
    f.write_text("FOO=bar\nBAZ=changed\nNEW=value\n")
    return str(f)


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
    args = parser.parse_args(["files", "a.env", "b.env", "--left-label", "prod", "--right-label", "staging"])
    assert args.left_label == "prod"
    assert args.right_label == "staging"


def test_run_files_no_differences(env_file_a):
    exit_code = run(["files", env_file_a, env_file_a, "--no-color"])
    assert exit_code == 0


def test_run_files_with_differences(env_file_a, env_file_b):
    exit_code = run(["files", env_file_a, env_file_b, "--no-color"])
    assert exit_code == 1


def test_run_uses_filenames_as_default_labels(env_file_a, env_file_b, capsys):
    run(["files", env_file_a, env_file_b, "--no-color"])
    captured = capsys.readouterr()
    assert os.path.basename(env_file_a) in captured.out or env_file_a in captured.out


def test_run_file_not_found(capsys):
    exit_code = run(["files", "nonexistent.env", "also_missing.env", "--no-color"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "error:" in captured.err


def test_run_current_subcommand(env_file_a):
    exit_code = run(["current", env_file_a, "--no-color"])
    assert exit_code in (0, 1)


def test_run_process_subcommand(env_file_a):
    fake_env = {"FOO": "bar", "BAZ": "qux"}
    with patch("envdiff.cli.load_from_process", return_value=fake_env):
        exit_code = run(["process", env_file_a, "1234", "--no-color"])
    assert exit_code in (0, 1)


def test_run_process_uses_pid_as_label(env_file_a, capsys):
    fake_env = {"FOO": "different"}
    with patch("envdiff.cli.load_from_process", return_value=fake_env):
        run(["process", env_file_a, "9999", "--no-color"])
    captured = capsys.readouterr()
    assert "9999" in captured.out
