"""Tests for envdiff.loader module."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from envdiff.loader import (
    load_from_file,
    load_from_string,
    load_current_process,
)


# --- load_from_file ---

def test_load_from_file_basic(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\nBAZ=qux\n")
    result = load_from_file(str(env_file))
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_load_from_file_with_quotes(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text('NAME="John Doe"\nGREET=\'hello\'\n')
    result = load_from_file(str(env_file))
    assert result["NAME"] == "John Doe"
    assert result["GREET"] == "hello"


def test_load_from_file_not_found():
    with pytest.raises(FileNotFoundError, match="env file not found"):
        load_from_file("/nonexistent/path/.env")


def test_load_from_file_is_directory(tmp_path: Path):
    with pytest.raises(IOError, match="path is not a file"):
        load_from_file(str(tmp_path))


def test_load_from_file_ignores_comments(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\nKEY=value\n")
    result = load_from_file(str(env_file))
    assert "# comment" not in result
    assert result.get("KEY") == "value"


def test_load_from_file_empty(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("")
    result = load_from_file(str(env_file))
    assert result == {}


# --- load_from_string ---

def test_load_from_string_basic():
    text = "HOST=localhost\nPORT=5432\n"
    result = load_from_string(text)
    assert result == {"HOST": "localhost", "PORT": "5432"}


def test_load_from_string_empty():
    result = load_from_string("")
    assert result == {}


def test_load_from_string_with_quotes():
    result = load_from_string('DB_URL="postgres://localhost/mydb"')
    assert result["DB_URL"] == "postgres://localhost/mydb"


# --- load_current_process ---

def test_load_current_process_returns_dict():
    result = load_current_process()
    assert isinstance(result, dict)


def test_load_current_process_contains_path():
    result = load_current_process()
    # PATH should be present in virtually any environment
    assert "PATH" in result


def test_load_current_process_matches_os_environ():
    result = load_current_process()
    assert result == dict(os.environ)
