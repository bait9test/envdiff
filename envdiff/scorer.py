"""Scores the similarity between two environment variable sets."""

from dataclasses import dataclass
from typing import Dict

from envdiff.differ import DiffResult


@dataclass
class SimilarityScore:
    total_keys: int
    matching_keys: int
    changed_keys: int
    only_in_left: int
    only_in_right: int
    score: float  # 0.0 to 1.0

    def as_percent(self) -> str:
        return f"{self.score * 100:.1f}%"

    def grade(self) -> str:
        if self.score >= 0.95:
            return "A"
        elif self.score >= 0.80:
            return "B"
        elif self.score >= 0.60:
            return "C"
        elif self.score >= 0.40:
            return "D"
        return "F"


def score_diff(result: DiffResult) -> SimilarityScore:
    """Compute a similarity score from a DiffResult."""
    matching = len(result.unchanged)
    changed = len(result.changed)
    left_only = len(result.only_in_left)
    right_only = len(result.only_in_right)

    total = matching + changed + left_only + right_only
    if total == 0:
        return SimilarityScore(
            total_keys=0,
            matching_keys=0,
            changed_keys=0,
            only_in_left=0,
            only_in_right=0,
            score=1.0,
        )

    raw_score = matching / total
    return SimilarityScore(
        total_keys=total,
        matching_keys=matching,
        changed_keys=changed,
        only_in_left=left_only,
        only_in_right=right_only,
        score=round(raw_score, 4),
    )


def score_envs(left: Dict[str, str], right: Dict[str, str]) -> SimilarityScore:
    """Convenience: score two raw env dicts directly."""
    from envdiff.differ import diff_envs
    return score_diff(diff_envs(left, right))
