"""Tests for envdiff.merger."""

import pytest
from envdiff.merger import (
    MergeConflictError,
    MergeStrategy,
    merge_envs,
    merge_origins,
)


A = {"FOO": "1", "BAR": "hello"}
B = {"FOO": "2", "BAZ": "world"}
C = {"BAR": "hi", "QUX": "42"}


def test_merge_empty_list():
    assert merge_envs([]) == {}


def test_merge_single():
    assert merge_envs([A]) == A


def test_merge_last_wins_on_conflict():
    result = merge_envs([A, B], strategy=MergeStrategy.LAST)
    assert result["FOO"] == "2"


def test_merge_first_wins_on_conflict():
    result = merge_envs([A, B], strategy=MergeStrategy.FIRST)
    assert result["FOO"] == "1"


def test_merge_non_conflicting_keys_included():
    result = merge_envs([A, B], strategy=MergeStrategy.LAST)
    assert "BAR" in result
    assert "BAZ" in result


def test_merge_three_sources():
    result = merge_envs([A, B, C], strategy=MergeStrategy.LAST)
    assert result["BAR"] == "hi"  # C overrides A
    assert result["FOO"] == "2"   # B overrides A
    assert result["QUX"] == "42"


def test_merge_strict_no_conflict():
    env1 = {"FOO": "1"}
    env2 = {"BAR": "2"}
    result = merge_envs([env1, env2], strategy=MergeStrategy.STRICT)
    assert result == {"FOO": "1", "BAR": "2"}


def test_merge_strict_same_value_no_error():
    env1 = {"FOO": "same"}
    env2 = {"FOO": "same"}
    result = merge_envs([env1, env2], strategy=MergeStrategy.STRICT)
    assert result["FOO"] == "same"


def test_merge_strict_raises_on_conflict():
    with pytest.raises(MergeConflictError, match="FOO"):
        merge_envs([A, B], strategy=MergeStrategy.STRICT)


def test_merge_strict_error_mentions_labels():
    with pytest.raises(MergeConflictError, match="source_a"):
        merge_envs([A, B], strategy=MergeStrategy.STRICT, labels=["source_a", "source_b"])


def test_merge_origins_single_source():
    origins = merge_origins([A], labels=["a"])
    assert origins["FOO"] == ["a"]
    assert origins["BAR"] == ["a"]


def test_merge_origins_multiple_sources():
    origins = merge_origins([A, B], labels=["a", "b"])
    assert origins["FOO"] == ["a", "b"]
    assert origins["BAR"] == ["a"]
    assert origins["BAZ"] == ["b"]


def test_merge_origins_default_labels():
    origins = merge_origins([A, B])
    assert "0" in origins["FOO"]
    assert "1" in origins["FOO"]
