"""Summarizer: produce a concise human-readable summary of an env diff."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from envdiff.differ import DiffResult
from envdiff.scorer import score_diff


@dataclass
class EnvSummary:
    total_keys: int
    only_in_left: int
    only_in_right: int
    changed: int
    unchanged: int
    similarity_percent: float
    grade: str
    headline: str

    def as_dict(self) -> dict:
        return {
            "total_keys": self.total_keys,
            "only_in_left": self.only_in_left,
            "only_in_right": self.only_in_right,
            "changed": self.changed,
            "unchanged": self.unchanged,
            "similarity_percent": self.similarity_percent,
            "grade": self.grade,
            "headline": self.headline,
        }


def _headline(only_left: int, only_right: int, changed: int) -> str:
    if only_left == 0 and only_right == 0 and changed == 0:
        return "Environments are identical."
    parts = []
    if only_left:
        parts.append(f"{only_left} key(s) only in left")
    if only_right:
        parts.append(f"{only_right} key(s) only in right")
    if changed:
        parts.append(f"{changed} value(s) changed")
    return "; ".join(parts) + "."


def summarize(result: DiffResult, label_left: str = "left", label_right: str = "right") -> EnvSummary:  # noqa: E501
    """Return an EnvSummary for the given DiffResult."""
    ol = len(result.only_in_left)
    or_ = len(result.only_in_right)
    ch = len(result.changed)
    unch = len(result.unchanged)
    total = ol + or_ + ch + unch

    sc = score_diff(result)
    return EnvSummary(
        total_keys=total,
        only_in_left=ol,
        only_in_right=or_,
        changed=ch,
        unchanged=unch,
        similarity_percent=sc.as_percent(),
        grade=sc.grade(),
        headline=_headline(ol, or_, ch),
    )


def format_summary(summary: EnvSummary, label_left: str = "left", label_right: str = "right") -> str:
    """Render an EnvSummary as a plain-text block."""
    lines = [
        f"Summary ({label_left} vs {label_right})",
        "-" * 36,
        summary.headline,
        f"  Total keys   : {summary.total_keys}",
        f"  Only in {label_left:<6}: {summary.only_in_left}",
        f"  Only in {label_right:<6}: {summary.only_in_right}",
        f"  Changed      : {summary.changed}",
        f"  Unchanged    : {summary.unchanged}",
        f"  Similarity   : {summary.similarity_percent:.1f}%  [{summary.grade}]",
    ]
    return "\n".join(lines)
