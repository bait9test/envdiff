"""Alerting hooks for watcher events — notify on env changes."""

import sys
from typing import Callable, List, Optional

from envdiff.differ import DiffResult
from envdiff.formatter import format_diff


AlertHandler = Callable[[DiffResult, str], None]


def stdout_alert(result: DiffResult, label: str = "change detected") -> None:
    """Print a formatted diff to stdout."""
    print(f"[envdiff] {label}")
    print(format_diff(result, color=False))


def stderr_alert(result: DiffResult, label: str = "change detected") -> None:
    """Print a formatted diff to stderr."""
    print(f"[envdiff] {label}", file=sys.stderr)
    print(format_diff(result, color=False), file=sys.stderr)


def threshold_alert(
    handler: AlertHandler,
    min_changes: int = 1,
) -> AlertHandler:
    """
    Wrap an alert handler so it only fires when the total number of
    differing keys meets or exceeds *min_changes*.
    """
    def _wrapped(result: DiffResult, label: str = "change detected") -> None:
        total = (
            len(result.only_in_left)
            + len(result.only_in_right)
            + len(result.changed)
        )
        if total >= min_changes:
            handler(result, label)

    return _wrapped


def key_filter_alert(
    handler: AlertHandler,
    watched_keys: List[str],
) -> AlertHandler:
    """
    Wrap an alert handler so it only fires when at least one of the
    *watched_keys* appears in the diff.
    """
    watched = set(watched_keys)

    def _wrapped(result: DiffResult, label: str = "change detected") -> None:
        affected = (
            set(result.only_in_left)
            | set(result.only_in_right)
            | set(result.changed)
        )
        if affected & watched:
            handler(result, label)

    return _wrapped


def multi_alert(handlers: List[AlertHandler]) -> AlertHandler:
    """Fan-out to multiple alert handlers."""
    def _wrapped(result: DiffResult, label: str = "change detected") -> None:
        for h in handlers:
            h(result, label)

    return _wrapped
