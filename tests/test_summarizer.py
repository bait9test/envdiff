"""Tests for envdiff.summarizer."""

from __future__ import annotations

import pytest

from envdiff.differ import DiffResult
from envdiff.summarizer import EnvSummary, summarize, format_summary, _headline


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        only_in_left={"A": "1", "B": "2"},
        only_in_right={"C": "3"},
        changed={"D": ("old", "new")},
        unchanged={"E": "5"},
    )


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(
        only_in_left={},
        only_in_right={},
        changed={},
        unchanged={"X": "1"},
    )


def test_summarize_counts(result: DiffResult) -> None:
    s = summarize(result)
    assert s.only_in_left == 2
    assert s.only_in_right == 1
    assert s.changed == 1
    assert s.unchanged == 1


def test_summarize_total_keys(result: DiffResult) -> None:
    s = summarize(result)
    assert s.total_keys == 5


def test_summarize_similarity_is_float(result: DiffResult) -> None:
    s = summarize(result)
    assert isinstance(s.similarity_percent, float)
    assert 0.0 <= s.similarity_percent <= 100.0


def test_summarize_grade_is_string(result: DiffResult) -> None:
    s = summarize(result)
    assert isinstance(s.grade, str)
    assert len(s.grade) > 0


def test_headline_identical(empty_result: DiffResult) -> None:
    s = summarize(empty_result)
    assert s.headline == "Environments are identical."


def test_headline_with_differences(result: DiffResult) -> None:
    s = summarize(result)
    assert "left" in s.headline
    assert "right" in s.headline
    assert "changed" in s.headline


def test_as_dict_keys(result: DiffResult) -> None:
    d = summarize(result).as_dict()
    expected = {"total_keys", "only_in_left", "only_in_right", "changed",
                "unchanged", "similarity_percent", "grade", "headline"}
    assert set(d.keys()) == expected


def test_format_summary_contains_labels(result: DiffResult) -> None:
    s = summarize(result)
    text = format_summary(s, label_left="prod", label_right="staging")
    assert "prod" in text
    assert "staging" in text


def test_format_summary_contains_counts(result: DiffResult) -> None:
    s = summarize(result)
    text = format_summary(s)
    assert str(s.total_keys) in text
    assert str(s.changed) in text


def test_format_summary_contains_similarity(result: DiffResult) -> None:
    s = summarize(result)
    text = format_summary(s)
    assert "%" in text
    assert s.grade in text


def test_headline_standalone() -> None:
    assert _headline(0, 0, 0) == "Environments are identical."
    h = _headline(1, 0, 2)
    assert "1 key(s) only in left" in h
    assert "2 value(s) changed" in h
