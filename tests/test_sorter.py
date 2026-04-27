"""Tests for envdiff.sorter."""

import pytest

from envdiff.differ import DiffResult
from envdiff.sorter import SortOrder, group_by_prefix, sorted_groups, sorted_keys


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        only_in_left={"ZEBRA": "1"},
        only_in_right={"APPLE": "2"},
        changed={"MONGO_URI": ("old", "new"), "DB_HOST": ("a", "b")},
        unchanged={"PORT": "3000"},
    )


def test_sorted_keys_alpha(result):
    keys = sorted_keys(result, order=SortOrder.ALPHA)
    assert keys == sorted(keys)


def test_sorted_keys_alpha_contains_all(result):
    keys = sorted_keys(result, order=SortOrder.ALPHA)
    assert set(keys) == {"ZEBRA", "APPLE", "MONGO_URI", "DB_HOST", "PORT"}


def test_sorted_keys_none_contains_all(result):
    keys = sorted_keys(result, order=SortOrder.NONE)
    assert set(keys) == {"ZEBRA", "APPLE", "MONGO_URI", "DB_HOST", "PORT"}


def test_sorted_keys_status_order(result):
    keys = sorted_keys(result, order=SortOrder.STATUS)
    # changed keys come before only_in_left, only_in_right, unchanged
    changed_idx = max(keys.index(k) for k in result.changed)
    only_left_idx = keys.index("ZEBRA")
    only_right_idx = keys.index("APPLE")
    unchanged_idx = keys.index("PORT")
    assert changed_idx < only_left_idx
    assert changed_idx < only_right_idx
    assert only_left_idx < unchanged_idx
    assert only_right_idx < unchanged_idx


def test_group_by_prefix_basic():
    keys = ["DB_HOST", "DB_PORT", "APP_NAME", "PORT"]
    groups = group_by_prefix(keys)
    assert groups["DB"] == ["DB_HOST", "DB_PORT"]
    assert groups["APP"] == ["APP_NAME"]
    assert groups[""] == ["PORT"]


def test_group_by_prefix_custom_separator():
    keys = ["aws.region", "aws.key", "debug"]
    groups = group_by_prefix(keys, separator=".")
    assert groups["aws"] == ["aws.region", "aws.key"]
    assert groups[""] == ["debug"]


def test_group_by_prefix_no_separator():
    keys = ["FOO", "BAR"]
    groups = group_by_prefix(keys)
    assert groups[""] == ["FOO", "BAR"]


def test_sorted_groups_returns_sorted_prefixes(result):
    groups = sorted_groups(result)
    prefixes = [prefix for prefix, _ in groups]
    assert prefixes == sorted(prefixes)


def test_sorted_groups_all_keys_present(result):
    groups = sorted_groups(result)
    all_keys = [k for _, keys in groups for k in keys]
    assert set(all_keys) == {"ZEBRA", "APPLE", "MONGO_URI", "DB_HOST", "PORT"}
