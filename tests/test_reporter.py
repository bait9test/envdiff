"""Tests for envdiff.reporter."""

import json

import pytest

from envdiff.differ import DiffResult
from envdiff.reporter import report


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        only_in_left={"ALPHA"},
        only_in_right={"BETA"},
        changed={"GAMMA": ("old", "new")},
        unchanged=["DELTA"],
    )


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(only_in_left=set(), only_in_right=set(), changed={}, unchanged=["X"])


# --- text format ---

def test_text_shows_only_in_left(result):
    out = report(result, fmt="text", labels=("a", "b"))
    assert "< ALPHA (only in a)" in out


def test_text_shows_only_in_right(result):
    out = report(result, fmt="text", labels=("a", "b"))
    assert "> BETA (only in b)" in out


def test_text_shows_changed(result):
    out = report(result, fmt="text", labels=("a", "b"))
    assert "~ GAMMA" in out
    assert "'old'" in out
    assert "'new'" in out


def test_text_no_diff(empty_result):
    out = report(empty_result, fmt="text")
    assert out == "No differences found."


# --- json format ---

def test_json_structure(result):
    out = report(result, fmt="json", labels=("left", "right"))
    data = json.loads(out)
    assert "only_in_left" in data
    assert "only_in_right" in data
    assert "changed" in data
    assert "unchanged" in data


def test_json_only_in_left(result):
    data = json.loads(report(result, fmt="json", labels=("left", "right")))
    assert "ALPHA" in data["only_in_left"]["keys"]


def test_json_changed_values(result):
    data = json.loads(report(result, fmt="json", labels=("left", "right")))
    changed = data["changed"]
    assert len(changed) == 1
    assert changed[0]["key"] == "GAMMA"
    assert changed[0]["left"] == "old"
    assert changed[0]["right"] == "new"


# --- markdown format ---

def test_markdown_heading(result):
    out = report(result, fmt="markdown")
    assert "# Environment Diff Report" in out


def test_markdown_only_sections(result):
    out = report(result, fmt="markdown", labels=("dev", "prod"))
    assert "## Only in `dev`" in out
    assert "## Only in `prod`" in out


def test_markdown_changed_table(result):
    out = report(result, fmt="markdown")
    assert "## Changed Values" in out
    assert "| Key |" in out
    assert "GAMMA" in out


def test_markdown_no_diff(empty_result):
    out = report(empty_result, fmt="markdown")
    assert "_No differences found._" in out
