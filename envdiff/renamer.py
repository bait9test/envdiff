"""Rename keys across an env dict or a DiffResult."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from envdiff.differ import DiffResult


@dataclass
class RenameMap:
    """Holds old->new key rename rules."""
    rules: Dict[str, str]

    def add(self, old: str, new: str) -> None:
        self.rules[old] = new

    def reverse(self) -> "RenameMap":
        return RenameMap({v: k for k, v in self.rules.items()})

    def __len__(self) -> int:
        return len(self.rules)


def make_rename_map(rules: Dict[str, str]) -> RenameMap:
    """Construct a RenameMap from a plain dict."""
    return RenameMap(dict(rules))


def rename_env(
    env: Dict[str, str],
    rename_map: RenameMap,
    *,
    ignore_missing: bool = True,
) -> Dict[str, str]:
    """Return a new env dict with keys renamed according to *rename_map*.

    Keys not present in *rename_map* are passed through unchanged.
    If *ignore_missing* is False a KeyError is raised for any old key
    referenced in the map that does not exist in *env*.
    """
    result: Dict[str, str] = {}
    for key, value in env.items():
        new_key = rename_map.rules.get(key, key)
        result[new_key] = value

    if not ignore_missing:
        for old in rename_map.rules:
            if old not in env:
                raise KeyError(f"Key '{old}' not found in env")

    return result


def rename_diff(
    diff: DiffResult,
    rename_map: RenameMap,
) -> DiffResult:
    """Return a new DiffResult with keys renamed according to *rename_map*.

    Only renames keys; values and status are preserved.
    """
    def _rk(d: Dict[str, str]) -> Dict[str, str]:
        return {rename_map.rules.get(k, k): v for k, v in d.items()}

    def _rk2(d: Dict[str, tuple]) -> Dict[str, tuple]:
        return {rename_map.rules.get(k, k): v for k, v in d.items()}

    return DiffResult(
        only_in_left=_rk(diff.only_in_left),
        only_in_right=_rk(diff.only_in_right),
        changed=_rk2(diff.changed),
        unchanged=_rk(diff.unchanged),
    )
