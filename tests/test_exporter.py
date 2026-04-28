"""Tests for envdiff.exporter."""

import json
import pytest

from envdiff.differ import diff_envs
from envdiff.exporter import export_diff


@pytest.fixture
def result():
    left = {"A": "1", "B": "2", "C": "same"}
    right = {"B": "99", "C": "same", "D": "4"}
    return diff_envs(left, right)


# --- CSV ---

def test_csv_has_header(result):
    out = export_diff(result, "csv")
    assert out.splitlines()[0] == "key,status,left_value,right_value"


def test_csv_only_in_left(result):
    out = export_diff(result, "csv")
    assert "A,only_in_left,1," in out


def test_csv_only_in_right(result):
    out = export_diff(result, "csv")
    assert "D,only_in_right,,4" in out


def test_csv_changed(result):
    out = export_diff(result, "csv")
    assert "B,changed,2,99" in out


def test_csv_unchanged(result):
    out = export_diff(result, "csv")
    assert "C,unchanged,same,same" in out


# --- JSON ---

def test_json_is_valid(result):
    out = export_diff(result, "json")
    data = json.loads(out)  # should not raise
    assert isinstance(data, dict)


def test_json_keys_present(result):
    data = json.loads(export_diff(result, "json"))
    assert set(data.keys()) == {"only_in_left", "only_in_right", "changed", "unchanged"}


def test_json_changed_structure(result):
    data = json.loads(export_diff(result, "json"))
    assert data["changed"]["B"] == {"left": "2", "right": "99"}


def test_json_only_in_left_value(result):
    data = json.loads(export_diff(result, "json"))
    assert data["only_in_left"]["A"] == "1"


# --- dotenv ---

def test_dotenv_unchanged_key(result):
    out = export_diff(result, "dotenv")
    assert "C=same" in out


def test_dotenv_only_in_left_is_comment(result):
    out = export_diff(result, "dotenv")
    assert out.count("# A=") == 1


def test_dotenv_only_in_right_present(result):
    out = export_diff(result, "dotenv")
    assert "D=4" in out


def test_dotenv_changed_uses_right_value(result):
    out = export_diff(result, "dotenv")
    assert "B=99" in out


def test_dotenv_ends_with_newline(result):
    out = export_diff(result, "dotenv")
    assert out.endswith("\n")


# --- invalid format ---

def test_invalid_format_raises(result):
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_diff(result, "xml")  # type: ignore[arg-type]
