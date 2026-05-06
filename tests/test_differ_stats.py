"""Tests for envdiff.differ_stats."""
from __future__ import annotations

import pytest

from envdiff.differ import DiffResult
from envdiff.differ_stats import DiffStats, compute_stats, format_stats


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        only_in_left={"A": "1", "B": "2"},
        only_in_right={"C": "3"},
        changed={"D": ("old", "new")},
        unchanged={"E": "5", "F": "6"},
    )


def test_compute_stats_totals(result):
    stats = compute_stats(result)
    assert stats.total_keys == 6


def test_compute_stats_only_left(result):
    stats = compute_stats(result)
    assert stats.only_in_left == 2


def test_compute_stats_only_right(result):
    stats = compute_stats(result)
    assert stats.only_in_right == 1


def test_compute_stats_changed(result):
    stats = compute_stats(result)
    assert stats.changed == 1


def test_compute_stats_unchanged(result):
    stats = compute_stats(result)
    assert stats.unchanged == 2


def test_total_differences(result):
    stats = compute_stats(result)
    assert stats.total_differences == 4  # 2 + 1 + 1


def test_change_rate(result):
    stats = compute_stats(result)
    assert stats.change_rate == pytest.approx(4 / 6, rel=1e-3)


def test_change_rate_empty():
    empty = DiffResult({}, {}, {}, {})
    stats = compute_stats(empty)
    assert stats.change_rate == 0.0


def test_as_dict_keys(result):
    d = compute_stats(result).as_dict()
    assert set(d.keys()) == {
        "total_keys",
        "only_in_left",
        "only_in_right",
        "changed",
        "unchanged",
        "total_differences",
        "change_rate",
    }


def test_format_stats_contains_rate(result):
    stats = compute_stats(result)
    text = format_stats(stats)
    assert "Change rate" in text
    assert "%" in text


def test_format_stats_contains_counts(result):
    stats = compute_stats(result)
    text = format_stats(stats)
    assert "6" in text  # total
    assert "2" in text  # only_in_left
