"""Generate .env template files from existing env sets or diff results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envdiff.differ import DiffResult


@dataclass
class TemplateOptions:
    placeholder: str = "<FILL_ME>"
    include_values: bool = False
    include_comments: bool = True
    section_headers: bool = True


def env_to_template(
    env: dict[str, str],
    options: Optional[TemplateOptions] = None,
) -> str:
    """Convert a flat env dict into a template string."""
    opts = options or TemplateOptions()
    lines: list[str] = []
    for key in sorted(env):
        value = env[key] if opts.include_values else opts.placeholder
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n" if lines else ""


def diff_to_template(
    result: DiffResult,
    options: Optional[TemplateOptions] = None,
) -> str:
    """Build a merged template from a DiffResult, annotating discrepancies."""
    opts = options or TemplateOptions()
    lines: list[str] = []

    all_keys = sorted(
        set(result.only_in_left)
        | set(result.only_in_right)
        | set(result.changed)
        | set(result.unchanged)
    )

    for key in all_keys:
        if opts.include_comments:
            if key in result.only_in_left:
                lines.append("# only in left")
            elif key in result.only_in_right:
                lines.append("# only in right")
            elif key in result.changed:
                left_val, right_val = result.changed[key]
                lines.append(f"# changed: left={left_val!r}, right={right_val!r}")

        if opts.include_values and key in result.unchanged:
            value = result.unchanged[key]
        else:
            value = opts.placeholder

        lines.append(f"{key}={value}")

    return "\n".join(lines) + "\n" if lines else ""


def write_template(path: str, content: str) -> None:
    """Write template content to a file."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
