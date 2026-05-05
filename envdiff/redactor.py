"""Redact sensitive values in environment variable dicts."""

from __future__ import annotations

import re
from typing import Dict, Iterable, Optional

# Keys matching these patterns are considered sensitive by default
_DEFAULT_PATTERNS: list[str] = [
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*PASSWD.*",
    r".*TOKEN.*",
    r".*API_KEY.*",
    r".*PRIVATE_KEY.*",
    r".*CREDENTIALS.*",
]

REDACTED = "***REDACTED***"


def _compile(patterns: Iterable[str]) -> list[re.Pattern[str]]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def is_sensitive(
    key: str,
    patterns: Optional[Iterable[str]] = None,
) -> bool:
    """Return True if *key* matches any sensitive pattern."""
    compiled = _compile(patterns if patterns is not None else _DEFAULT_PATTERNS)
    return any(rx.fullmatch(key) for rx in compiled)


def redact(
    env: Dict[str, str],
    patterns: Optional[Iterable[str]] = None,
    placeholder: str = REDACTED,
) -> Dict[str, str]:
    """Return a copy of *env* with sensitive values replaced by *placeholder*."""
    result: Dict[str, str] = {}
    for key, value in env.items():
        result[key] = placeholder if is_sensitive(key, patterns) else value
    return result


def redact_diff(
    diff: "DiffResult",  # type: ignore[name-defined]  # noqa: F821
    patterns: Optional[Iterable[str]] = None,
    placeholder: str = REDACTED,
) -> "DiffResult":  # type: ignore[name-defined]  # noqa: F821
    """Return a new DiffResult with sensitive changed-values replaced."""
    from envdiff.differ import DiffResult

    redacted_changed = {}
    for key, (left, right) in diff.changed.items():
        if is_sensitive(key, patterns):
            redacted_changed[key] = (placeholder, placeholder)
        else:
            redacted_changed[key] = (left, right)

    return DiffResult(
        only_in_left=dict(diff.only_in_left),
        only_in_right=dict(diff.only_in_right),
        changed=redacted_changed,
        unchanged=dict(diff.unchanged),
    )
