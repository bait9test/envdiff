"""Lint .env files for common style and correctness issues."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class LintIssue:
    line: int
    key: str
    code: str
    message: str

    def __str__(self) -> str:
        return f"Line {self.line} [{self.code}] {self.key!r}: {self.message}"


@dataclass
class LintResult:
    issues: list[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    def __len__(self) -> int:
        return len(self.issues)

    def by_code(self, code: str) -> list[LintIssue]:
        return [i for i in self.issues if i.code == code]


def lint_env(env: dict[str, str], source_lines: list[str] | None = None) -> LintResult:
    """Run all lint checks against an env dict.

    source_lines, if provided, are the raw lines from the .env file and
    enable line-number reporting.
    """
    result = LintResult()
    line_map = _build_line_map(source_lines) if source_lines else {}

    for key, value in env.items():
        lineno = line_map.get(key, 0)

        if key != key.upper():
            result.issues.append(LintIssue(lineno, key, "E001", "Key should be uppercase"))

        if key != key.strip():
            result.issues.append(LintIssue(lineno, key, "E002", "Key has leading or trailing whitespace"))

        if " " in key:
            result.issues.append(LintIssue(lineno, key, "E003", "Key contains spaces"))

        if value == "":
            result.issues.append(LintIssue(lineno, key, "W001", "Value is empty"))

        if value != value.strip() and value != "":
            result.issues.append(LintIssue(lineno, key, "W002", "Value has leading or trailing whitespace"))

        if len(value) > 512:
            result.issues.append(LintIssue(lineno, key, "W003", "Value is unusually long (>512 chars)"))

    return result


def lint_file(path: str) -> LintResult:
    """Parse and lint a .env file, preserving line numbers."""
    from envdiff.parser import parse_env_file

    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    env = parse_env_file(path)
    return lint_env(env, source_lines=lines)


def _build_line_map(lines: Iterable[str]) -> dict[str, int]:
    """Map key names to their 1-based line numbers."""
    mapping: dict[str, int] = {}
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            mapping.setdefault(key, i)
    return mapping
