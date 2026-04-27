"""Formatters for rendering DiffResult output."""

from typing import Optional
from envdiff.differ import DiffResult

ANSI_RED = "\033[91m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RESET = "\033[0m"


def format_diff(
    result: DiffResult,
    left_label: str = "left",
    right_label: str = "right",
    color: bool = True,
    show_unchanged: bool = False,
) -> str:
    """Format a DiffResult into a human-readable string."""
    lines = []

    def _c(text: str, code: str) -> str:
        return f"{code}{text}{ANSI_RESET}" if color else text

    if result.only_in_left:
        lines.append(f"Keys only in [{left_label}]:")
        for k, v in sorted(result.only_in_left.items()):
            lines.append(_c(f"  - {k}={v}", ANSI_RED))

    if result.only_in_right:
        lines.append(f"Keys only in [{right_label}]:")
        for k, v in sorted(result.only_in_right.items()):
            lines.append(_c(f"  + {k}={v}", ANSI_GREEN))

    if result.changed:
        lines.append("Changed values:")
        for k, (lv, rv) in sorted(result.changed.items()):
            lines.append(_c(f"  ~ {k}", ANSI_YELLOW))
            lines.append(_c(f"      [{left_label}]: {lv}", ANSI_RED))
            lines.append(_c(f"      [{right_label}]: {rv}", ANSI_GREEN))

    if show_unchanged and result.unchanged:
        lines.append("Unchanged keys:")
        for k, v in sorted(result.unchanged.items()):
            lines.append(f"    {k}={v}")

    if not result.has_differences:
        lines.append("No differences found.")

    return "\n".join(lines)
