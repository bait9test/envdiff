"""Generate structured reports from diff results in multiple formats."""

from __future__ import annotations

import json
from typing import Literal

from envdiff.differ import DiffResult

ReportFormat = Literal["json", "markdown", "text"]


def report(result: DiffResult, fmt: ReportFormat = "text", labels: tuple[str, str] = ("left", "right")) -> str:
    """Generate a report string for a DiffResult in the requested format."""
    if fmt == "json":
        return _report_json(result, labels)
    elif fmt == "markdown":
        return _report_markdown(result, labels)
    else:
        return _report_text(result, labels)


def _report_json(result: DiffResult, labels: tuple[str, str]) -> str:
    left_label, right_label = labels
    data = {
        "only_in_left": {
            "label": left_label,
            "keys": sorted(result.only_in_left),
        },
        "only_in_right": {
            "label": right_label,
            "keys": sorted(result.only_in_right),
        },
        "changed": [
            {"key": k, left_label: v[0], right_label: v[1]}
            for k, v in sorted(result.changed.items())
        ],
        "unchanged": sorted(result.unchanged),
    }
    return json.dumps(data, indent=2)


def _report_markdown(result: DiffResult, labels: tuple[str, str]) -> str:
    left_label, right_label = labels
    lines: list[str] = ["# Environment Diff Report", ""]

    if result.only_in_left:
        lines.append(f"## Only in `{left_label}`")
        for key in sorted(result.only_in_left):
            lines.append(f"- `{key}`")
        lines.append("")

    if result.only_in_right:
        lines.append(f"## Only in `{right_label}`")
        for key in sorted(result.only_in_right):
            lines.append(f"- `{key}`")
        lines.append("")

    if result.changed:
        lines.append("## Changed Values")
        lines.append(f"| Key | {left_label} | {right_label} |")
        lines.append("|-----|------|-------|")
        for key, (lv, rv) in sorted(result.changed.items()):
            lines.append(f"| `{key}` | `{lv}` | `{rv}` |")
        lines.append("")

    if not result.only_in_left and not result.only_in_right and not result.changed:
        lines.append("_No differences found._")
        lines.append("")

    return "\n".join(lines)


def _report_text(result: DiffResult, labels: tuple[str, str]) -> str:
    left_label, right_label = labels
    lines: list[str] = []

    for key in sorted(result.only_in_left):
        lines.append(f"< {key} (only in {left_label})")
    for key in sorted(result.only_in_right):
        lines.append(f"> {key} (only in {right_label})")
    for key, (lv, rv) in sorted(result.changed.items()):
        lines.append(f"~ {key}: {left_label}={lv!r} | {right_label}={rv!r}")

    if not lines:
        return "No differences found."
    return "\n".join(lines)
