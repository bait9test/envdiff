"""Tests for envdiff.scorer."""

import pytest
from envdiff.differ import DiffResult
from envdiff.scorer import SimilarityScore, score_diff, score_envs


@pytest.fixture
def perfect_result():
    return DiffResult(
        only_in_left={},
        only_in_right={},
        changed={},
        unchanged={"A": "1", "B": "2"},
    )


@pytest.fixture
def partial_result():
    return DiffResult(
        only_in_left={"X": "10"},
        only_in_right={"Y": "20"},
        changed={"B": ("old", "new")},
        unchanged={"A": "1"},
    )


def test_score_perfect_match(perfect_result):
    s = score_diff(perfect_result)
    assert s.score == 1.0


def test_score_perfect_grade(perfect_result):
    s = score_diff(perfect_result)
    assert s.grade() == "A"


def test_score_partial_total_keys(partial_result):
    s = score_diff(partial_result)
    assert s.total_keys == 4


def test_score_partial_matching(partial_result):
    s = score_diff(partial_result)
    assert s.matching_keys == 1


def test_score_partial_value(partial_result):
    s = score_diff(partial_result)
    assert s.score == 0.25


def test_score_empty_result():
    empty = DiffResult(only_in_left={}, only_in_right={}, changed={}, unchanged={})
    s = score_diff(empty)
    assert s.score == 1.0
    assert s.total_keys == 0


def test_as_percent(perfect_result):
    s = score_diff(perfect_result)
    assert s.as_percent() == "100.0%"


def test_as_percent_partial(partial_result):
    s = score_diff(partial_result)
    assert s.as_percent() == "25.0%"


def test_grade_f():
    result = DiffResult(
        only_in_left={"A": "1", "B": "2", "C": "3"},
        only_in_right={"D": "4", "E": "5", "F": "6"},
        changed={},
        unchanged={},
    )
    s = score_diff(result)
    assert s.grade() == "F"


def test_score_envs_identical():
    env = {"KEY": "val", "OTHER": "x"}
    s = score_envs(env, env.copy())
    assert s.score == 1.0


def test_score_envs_completely_different():
    s = score_envs({"A": "1"}, {"B": "2"})
    assert s.score == 0.0
    assert s.grade() == "F"


def test_score_envs_partial():
    left = {"A": "1", "B": "2"}
    right = {"A": "1", "B": "changed"}
    s = score_envs(left, right)
    assert s.matching_keys == 1
    assert s.changed_keys == 1
