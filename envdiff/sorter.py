"""Utilities for sorting and grouping diff results."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Tuple

from envdiff.differ import DiffResult


class SortOrder(str, Enum):
    ALPHA = "alpha"
    STATUS = "status"
    NONE = "none"


def sorted_keys(
    result: DiffResult,
    order: SortOrder = SortOrder.ALPHA,
) -> List[str]:
    """Return all keys from a DiffResult in the requested order."""
    all_keys = (
        set(result.only_in_left)
        | set(result.only_in_right)
        | set(result.changed)
        | set(result.unchanged)
    )

    if order == SortOrder.NONE:
        return list(all_keys)

    if order == SortOrder.ALPHA:
        return sorted(all_keys)

    if order == SortOrder.STATUS:
        # Group: changed first, then only_in_left, only_in_right, unchanged
        changed = sorted(result.changed.keys())
        only_left = sorted(result.only_in_left.keys())
        only_right = sorted(result.only_in_right.keys())
        unchanged = sorted(result.unchanged.keys())
        return changed + only_left + only_right + unchanged

    return sorted(all_keys)


def group_by_prefix(
    keys: List[str],
    separator: str = "_",
) -> Dict[str, List[str]]:
    """Group a list of env var keys by their first prefix segment.

    Keys without a separator are placed under the empty-string group.
    """
    groups: Dict[str, List[str]] = {}
    for key in keys:
        if separator in key:
            prefix = key.split(separator, 1)[0]
        else:
            prefix = ""
        groups.setdefault(prefix, []).append(key)
    return groups


def sorted_groups(
    result: DiffResult,
    order: SortOrder = SortOrder.ALPHA,
    separator: str = "_",
) -> List[Tuple[str, List[str]]]:
    """Return keys grouped by prefix, with groups sorted alphabetically."""
    keys = sorted_keys(result, order=order)
    groups = group_by_prefix(keys, separator=separator)
    return sorted(groups.items())
