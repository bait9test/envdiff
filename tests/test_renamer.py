"""Tests for envdiff.renamer."""
import pytest

from envdiff.differ import DiffResult
from envdiff.renamer import (
    RenameMap,
    make_rename_map,
    rename_env,
    rename_diff,
)


# ---------------------------------------------------------------------------
# RenameMap
# ---------------------------------------------------------------------------

def test_rename_map_add():
    rm = RenameMap({})
    rm.add("OLD", "NEW")
    assert rm.rules["OLD"] == "NEW"


def test_rename_map_len():
    rm = make_rename_map({"A": "B", "C": "D"})
    assert len(rm) == 2


def test_rename_map_reverse():
    rm = make_rename_map({"A": "B"})
    rev = rm.reverse()
    assert rev.rules["B"] == "A"


# ---------------------------------------------------------------------------
# rename_env
# ---------------------------------------------------------------------------

def test_rename_env_basic():
    env = {"OLD_KEY": "value", "KEEP": "same"}
    rm = make_rename_map({"OLD_KEY": "NEW_KEY"})
    result = rename_env(env, rm)
    assert "NEW_KEY" in result
    assert "OLD_KEY" not in result
    assert result["NEW_KEY"] == "value"
    assert result["KEEP"] == "same"


def test_rename_env_passthrough_unmapped():
    env = {"A": "1", "B": "2"}
    rm = make_rename_map({"A": "Z"})
    result = rename_env(env, rm)
    assert result["B"] == "2"


def test_rename_env_ignore_missing_default():
    env = {"A": "1"}
    rm = make_rename_map({"MISSING": "NEW"})
    # should not raise
    result = rename_env(env, rm)
    assert result == {"A": "1"}


def test_rename_env_strict_raises_on_missing():
    env = {"A": "1"}
    rm = make_rename_map({"MISSING": "NEW"})
    with pytest.raises(KeyError, match="MISSING"):
        rename_env(env, rm, ignore_missing=False)


def test_rename_env_empty_map():
    env = {"X": "y"}
    rm = make_rename_map({})
    assert rename_env(env, rm) == {"X": "y"}


# ---------------------------------------------------------------------------
# rename_diff
# ---------------------------------------------------------------------------

@pytest.fixture()
def diff():
    return DiffResult(
        only_in_left={"LEFT_KEY": "lv"},
        only_in_right={"RIGHT_KEY": "rv"},
        changed={"CHANGED": ("old", "new")},
        unchanged={"SAME": "sv"},
    )


def test_rename_diff_only_in_left(diff):
    rm = make_rename_map({"LEFT_KEY": "LEFT_RENAMED"})
    result = rename_diff(diff, rm)
    assert "LEFT_RENAMED" in result.only_in_left
    assert "LEFT_KEY" not in result.only_in_left


def test_rename_diff_only_in_right(diff):
    rm = make_rename_map({"RIGHT_KEY": "RIGHT_RENAMED"})
    result = rename_diff(diff, rm)
    assert "RIGHT_RENAMED" in result.only_in_right


def test_rename_diff_changed(diff):
    rm = make_rename_map({"CHANGED": "CHANGED_RENAMED"})
    result = rename_diff(diff, rm)
    assert "CHANGED_RENAMED" in result.changed
    assert result.changed["CHANGED_RENAMED"] == ("old", "new")


def test_rename_diff_unchanged(diff):
    rm = make_rename_map({"SAME": "SAME_RENAMED"})
    result = rename_diff(diff, rm)
    assert "SAME_RENAMED" in result.unchanged


def test_rename_diff_empty_map_leaves_diff_intact(diff):
    rm = make_rename_map({})
    result = rename_diff(diff, rm)
    assert result.only_in_left == diff.only_in_left
    assert result.changed == diff.changed
