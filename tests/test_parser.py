"""Tests for envdiff.parser — .env file parsing."""

import pytest
from pathlib import Path
from textwrap import dedent

from envdiff.parser import parse_env_file, parse_env_string, _strip_quotes


# ---------------------------------------------------------------------------
# _strip_quotes
# ---------------------------------------------------------------------------

def test_strip_double_quotes():
    assert _strip_quotes('"hello world"') == "hello world"


def test_strip_single_quotes():
    assert _strip_quotes("'hello world'") == "hello world"


def test_no_quotes_unchanged():
    assert _strip_quotes("plain") == "plain"


def test_mismatched_quotes_unchanged():
    assert _strip_quotes("'mixed\"") == "'mixed\""


# ---------------------------------------------------------------------------
# parse_env_string
# ---------------------------------------------------------------------------

SAMPLE = dedent("""\
    # this is a comment
    APP_ENV=production
    DB_HOST="localhost"
    DB_PORT='5432'
    SECRET_KEY=abc123

    # another comment
    EMPTY_VAR=
""")


def test_parse_basic_keys():
    result = parse_env_string(SAMPLE)
    assert result["APP_ENV"] == "production"
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"
    assert result["SECRET_KEY"] == "abc123"


def test_empty_value_parsed():
    result = parse_env_string(SAMPLE)
    assert result["EMPTY_VAR"] == ""


def test_comments_ignored():
    result = parse_env_string(SAMPLE)
    assert all(not k.startswith("#") for k in result)


def test_blank_lines_ignored():
    result = parse_env_string("\n\n  \nFOO=bar\n")
    assert result == {"FOO": "bar"}


def test_malformed_line_skipped():
    result = parse_env_string("this is not valid\nGOOD=yes")
    assert result == {"GOOD": "yes"}


# ---------------------------------------------------------------------------
# parse_env_file
# ---------------------------------------------------------------------------

def test_parse_env_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("HOST=example.com\nPORT=8080\n", encoding="utf-8")
    result = parse_env_file(env_file)
    assert result == {"HOST": "example.com", "PORT": "8080"}


def test_parse_env_file_not_found(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        parse_env_file(tmp_path / "missing.env")
