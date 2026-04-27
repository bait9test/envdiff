"""Core diffing logic for comparing environment variable sets."""

from dataclasses import dataclass, field
from typing import Dict, Optional, Set


@dataclass
class DiffResult:
    """Holds the result of comparing two env sets."""

    only_in_left: Dict[str, str] = field(default_factory=dict)
    only_in_right: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (left_val, right_val)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(self.only_in_left or self.only_in_right or self.changed)

    def summary(self) -> str:
        lines = []
        if self.only_in_left:
            lines.append(f"  Only in left:  {len(self.only_in_left)} key(s)")
        if self.only_in_right:
            lines.append(f"  Only in right: {len(self.only_in_right)} key(s)")
        if self.changed:
            lines.append(f"  Changed:       {len(self.changed)} key(s)")
        if self.unchanged:
            lines.append(f"  Unchanged:     {len(self.unchanged)} key(s)")
        return "\n".join(lines) if lines else "  No differences found."


def diff_envs(
    left: Dict[str, str],
    right: Dict[str, str],
    ignore_keys: Optional[Set[str]] = None,
) -> DiffResult:
    """Compare two env dicts and return a DiffResult.

    Args:
        left: First environment variable mapping.
        right: Second environment variable mapping.
        ignore_keys: Optional set of keys to exclude from comparison.

    Returns:
        A DiffResult describing the differences.
    """
    ignore_keys = ignore_keys or set()

    left_filtered = {k: v for k, v in left.items() if k not in ignore_keys}
    right_filtered = {k: v for k, v in right.items() if k not in ignore_keys}

    left_keys = set(left_filtered)
    right_keys = set(right_filtered)

    result = DiffResult()

    result.only_in_left = {k: left_filtered[k] for k in left_keys - right_keys}
    result.only_in_right = {k: right_filtered[k] for k in right_keys - left_keys}

    for key in left_keys & right_keys:
        lv, rv = left_filtered[key], right_filtered[key]
        if lv != rv:
            result.changed[key] = (lv, rv)
        else:
            result.unchanged[key] = lv

    return result
