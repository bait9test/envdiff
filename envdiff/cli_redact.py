"""CLI sub-command: redact — print a .env file with sensitive values hidden."""

from __future__ import annotations

import argparse
import sys

from envdiff.loader import load_from_file
from envdiff.redactor import redact, _DEFAULT_PATTERNS


def add_redact_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "redact",
        help="Print a .env file with sensitive values replaced.",
    )
    p.add_argument("file", help="Path to the .env file to redact.")
    p.add_argument(
        "--placeholder",
        default="***REDACTED***",
        help="String to substitute for sensitive values (default: ***REDACTED***).",
    )
    p.add_argument(
        "--pattern",
        dest="patterns",
        action="append",
        metavar="REGEX",
        help=(
            "Additional regex pattern to treat as sensitive "
            "(can be repeated; replaces defaults when provided)."
        ),
    )
    p.add_argument(
        "--show-keys",
        action="store_true",
        default=False,
        help="List the keys that were redacted to stderr.",
    )
    p.set_defaults(func=run_redact)


def run_redact(args: argparse.Namespace) -> int:
    try:
        env = load_from_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    except IsADirectoryError:
        print(f"error: path is a directory: {args.file}", file=sys.stderr)
        return 1

    patterns = args.patterns if args.patterns else _DEFAULT_PATTERNS
    redacted = redact(env, patterns=patterns, placeholder=args.placeholder)

    if args.show_keys:
        hidden = [k for k in redacted if redacted[k] == args.placeholder]
        if hidden:
            print("Redacted keys: " + ", ".join(sorted(hidden)), file=sys.stderr)

    for key, value in redacted.items():
        print(f"{key}={value}")

    return 0
