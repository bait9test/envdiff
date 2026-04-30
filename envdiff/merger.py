"""Merge multiple env dicts into one, with configurable conflict resolution."""

from enum import Enum
from typing import Dict, List, Optional


class MergeStrategy(str, Enum):
    FIRST = "first"   # keep value from first source that defines the key
    LAST = "last"    # keep value from last source that defines the key
    STRICT = "strict"  # raise on any conflict


class MergeConflictError(Exception):
    """Raised when STRICT strategy encounters a conflicting key."""


def merge_envs(
    envs: List[Dict[str, str]],
    strategy: MergeStrategy = MergeStrategy.LAST,
    labels: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Merge a list of env dicts into a single dict.

    Args:
        envs: Ordered list of env dicts to merge.
        strategy: How to handle conflicting keys.
        labels: Optional source labels used in error messages.

    Returns:
        Merged env dict.
    """
    if not envs:
        return {}

    labels = labels or [str(i) for i in range(len(envs))]
    merged: Dict[str, str] = {}
    origins: Dict[str, str] = {}  # key -> label that set it

    for label, env in zip(labels, envs):
        for key, value in env.items():
            if key in merged:
                if strategy == MergeStrategy.STRICT and merged[key] != value:
                    raise MergeConflictError(
                        f"Conflict on key '{key}': "
                        f"'{origins[key]}' has '{merged[key]}', "
                        f"'{label}' has '{value}'"
                    )
                if strategy == MergeStrategy.LAST:
                    merged[key] = value
                    origins[key] = label
                # FIRST: keep existing, do nothing
            else:
                merged[key] = value
                origins[key] = label

    return merged


def merge_origins(
    envs: List[Dict[str, str]],
    labels: Optional[List[str]] = None,
) -> Dict[str, List[str]]:
    """Return a mapping of key -> list of labels that define it."""
    labels = labels or [str(i) for i in range(len(envs))]
    origins: Dict[str, List[str]] = {}
    for label, env in zip(labels, envs):
        for key in env:
            origins.setdefault(key, []).append(label)
    return origins
