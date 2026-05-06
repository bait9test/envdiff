"""Statistical analysis of diff results."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from envdiff.differ import DiffResult


@dataclass
class DiffStats:
    total_keys: int
    only_in_left: int
    only_in_right: int
    changed: int
    unchanged: int

    @property
    def total_differences(self) -> int:
        return self.only_in_left + self.only_in_right + self.changed

    @property
    def change_rate(self) -> float:
        """Fraction of total keys that differ (0.0 – 1.0)."""
        if self.total_keys == 0:
            return 0.0
        return self.total_differences / self.total_keys

    def as_dict(self) -> Dict[str, int | float]:
        return {
            "total_keys": self.total_keys,
            "only_in_left": self.only_in_left,
            "only_in_right": self.only_in_right,
            "changed": self.changed,
            "unchanged": self.unchanged,
            "total_differences": self.total_differences,
            "change_rate": round(self.change_rate, 4),
        }


def compute_stats(result: DiffResult) -> DiffStats:
    """Derive counts from a DiffResult."""
    only_left = len(result.only_in_left)
    only_right = len(result.only_in_right)
    changed = len(result.changed)
    unchanged = len(result.unchanged)
    total = only_left + only_right + changed + unchanged
    return DiffStats(
        total_keys=total,
        only_in_left=only_left,
        only_in_right=only_right,
        changed=changed,
        unchanged=unchanged,
    )


def format_stats(stats: DiffStats, *, color: bool = True) -> str:
    """Return a human-readable stats block."""
    pct = f"{stats.change_rate * 100:.1f}%"
    lines = [
        f"Total keys   : {stats.total_keys}",
        f"Only in left : {stats.only_in_left}",
        f"Only in right: {stats.only_in_right}",
        f"Changed      : {stats.changed}",
        f"Unchanged    : {stats.unchanged}",
        f"Change rate  : {pct}",
    ]
    return "\n".join(lines)
