"""Apply a diff as a patch to produce a merged .env output."""

from __future__ import annotations

from typing import Dict, Optional

from envdiff.differ import DiffResult


def patch_env(
    base: Dict[str, str],
    diff: DiffResult,
    *,
    apply_additions: bool = True,
    apply_removals: bool = False,
    apply_changes: bool = True,
) -> Dict[str, str]:
    """Return a new env dict by applying *diff* on top of *base*.

    Parameters
    ----------
    base:
        The environment to patch (typically the "left" side of the diff).
    diff:
        A :class:`~envdiff.differ.DiffResult` produced by :func:`~envdiff.differ.diff_envs`.
    apply_additions:
        When *True* (default), keys that exist only in the right side are added.
    apply_removals:
        When *True*, keys that exist only in the left side are removed.
    apply_changes:
        When *True* (default), changed values are updated to the right-side value.
    """
    result = dict(base)

    if apply_additions:
        for key, value in diff.only_in_right.items():
            result[key] = value

    if apply_removals:
        for key in diff.only_in_left:
            result.pop(key, None)

    if apply_changes:
        for key, (_, right_val) in diff.changed.items():
            result[key] = right_val

    return result


def patch_to_dotenv(env: Dict[str, str], *, quote_values: bool = True) -> str:
    """Serialise *env* to a .env-formatted string.

    Values containing spaces or special characters are double-quoted when
    *quote_values* is *True*.
    """
    lines: list[str] = []
    for key, value in sorted(env.items()):
        if quote_values and any(ch in value for ch in (" ", "\t", "#", "'", '"')):
            value = '"' + value.replace('"', '\\"') + '"'
        lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def write_patch(
    base: Dict[str, str],
    diff: DiffResult,
    path: str,
    *,
    apply_additions: bool = True,
    apply_removals: bool = False,
    apply_changes: bool = True,
    quote_values: bool = True,
) -> None:
    """Patch *base* with *diff* and write the result to *path*."""
    patched = patch_env(
        base,
        diff,
        apply_additions=apply_additions,
        apply_removals=apply_removals,
        apply_changes=apply_changes,
    )
    content = patch_to_dotenv(patched, quote_values=quote_values)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
