"""Export diff results to various file formats."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from envdiff.differ import DiffResult

ExportFormat = Literal["csv", "json", "dotenv"]


def export_diff(result: DiffResult, fmt: ExportFormat) -> str:
    """Export a DiffResult to the given format string."""
    if fmt == "csv":
        return _export_csv(result)
    if fmt == "json":
        return _export_json(result)
    if fmt == "dotenv":
        return _export_dotenv(result)
    raise ValueError(f"Unsupported export format: {fmt!r}")


def _export_csv(result: DiffResult) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "status", "left_value", "right_value"])

    for key in sorted(result.only_in_left):
        writer.writerow([key, "only_in_left", result.left.get(key, ""), ""])

    for key in sorted(result.only_in_right):
        writer.writerow([key, "only_in_right", "", result.right.get(key, "")])

    for key in sorted(result.changed):
        left_val, right_val = result.changed[key]
        writer.writerow([key, "changed", left_val, right_val])

    for key in sorted(result.unchanged):
        writer.writerow([key, "unchanged", result.left.get(key, ""), result.right.get(key, "")])

    return buf.getvalue()


def _export_json(result: DiffResult) -> str:
    data = {
        "only_in_left": {k: result.left[k] for k in sorted(result.only_in_left)},
        "only_in_right": {k: result.right[k] for k in sorted(result.only_in_right)},
        "changed": {
            k: {"left": lv, "right": rv}
            for k, (lv, rv) in sorted(result.changed.items())
        },
        "unchanged": {k: result.left[k] for k in sorted(result.unchanged)},
    }
    return json.dumps(data, indent=2)


def _export_dotenv(result: DiffResult) -> str:
    """Export the right-hand side values, merging left-only keys as comments."""
    lines: list[str] = []

    for key in sorted(result.only_in_left):
        lines.append(f"# {key}={result.left[key]}  # only in left")

    for key in sorted(result.only_in_right):
        lines.append(f"{key}={result.right[key]}")

    for key, (_, right_val) in sorted(result.changed.items()):
        lines.append(f"{key}={right_val}")

    for key in sorted(result.unchanged):
        lines.append(f"{key}={result.left[key]}")

    return "\n".join(lines) + ("\n" if lines else "")
