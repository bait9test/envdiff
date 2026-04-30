"""CLI subcommand: validate env files against rules."""

from __future__ import annotations

import argparse
import sys
from typing import List

from envdiff.loader import load_from_file
from envdiff.validator import (
    rule_key_uppercase,
    rule_not_empty,
    rule_no_spaces_in_key,
    validate_env,
)

_BUILTIN_RULES = {
    "not_empty": rule_not_empty,
    "no_spaces_in_key": rule_no_spaces_in_key,
    "key_uppercase": rule_key_uppercase,
}


def add_validate_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "validate",
        help="Validate keys/values in one or more .env files",
    )
    p.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help=".env file(s) to validate",
    )
    p.add_argument(
        "--rules",
        nargs="+",
        metavar="RULE",
        choices=list(_BUILTIN_RULES.keys()),
        default=["not_empty", "no_spaces_in_key"],
        help="Rules to apply (default: not_empty no_spaces_in_key)",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero status if any errors are found",
    )
    p.set_defaults(func=run_validate)


def run_validate(args: argparse.Namespace) -> int:
    rules = [_BUILTIN_RULES[r] for r in args.rules]
    all_valid = True

    for path in args.files:
        try:
            env = load_from_file(path)
        except (FileNotFoundError, IsADirectoryError) as exc:
            print(f"[error] {exc}", file=sys.stderr)
            return 2

        result = validate_env(env, rules=rules)
        if result.valid:
            print(f"[ok] {path}")
        else:
            all_valid = False
            print(f"[fail] {path}")
            for err in result.errors:
                print(f"  - {err}")

    if args.strict and not all_valid:
        return 1
    return 0
