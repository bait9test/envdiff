"""CLI subcommand: lint — check .env files for style issues."""

from __future__ import annotations

import argparse
import sys

from envdiff.linter import lint_file, LintResult


def add_lint_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "lint",
        help="Check a .env file for style and correctness issues.",
    )
    p.add_argument("file", help="Path to the .env file to lint.")
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with code 1 even for warnings (W-codes).",
    )
    p.add_argument(
        "--ignore",
        metavar="CODE",
        action="append",
        default=[],
        help="Suppress a specific issue code (repeatable).",
    )
    p.set_defaults(func=run_lint)


def run_lint(args: argparse.Namespace) -> int:
    """Entry point for the lint subcommand. Returns an exit code."""
    try:
        result = lint_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    ignored: set[str] = set(args.ignore)
    visible = [i for i in result.issues if i.code not in ignored]

    if not visible:
        print(f"{args.file}: OK (no issues found)")
        return 0

    for issue in visible:
        print(str(issue))

    errors = [i for i in visible if i.code.startswith("E")]
    warnings = [i for i in visible if i.code.startswith("W")]

    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s) in {args.file}")

    if errors:
        return 1
    if warnings and args.strict:
        return 1
    return 0
