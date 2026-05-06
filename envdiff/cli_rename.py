"""CLI sub-command: rename keys in an .env file."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envdiff.loader import load_from_file
from envdiff.renamer import make_rename_map, rename_env


def add_rename_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "rename",
        help="Rename keys in an .env file and print the result.",
    )
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--rule",
        metavar="OLD=NEW",
        action="append",
        dest="rules",
        default=[],
        help="Rename rule in OLD=NEW format (repeatable)",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Error if a rule references a key not present in the file",
    )
    p.add_argument(
        "--format",
        choices=["dotenv", "keys"],
        default="dotenv",
        dest="fmt",
        help="Output format (default: dotenv)",
    )
    p.set_defaults(func=run_rename)


def _parse_rules(raw: List[str]) -> dict:
    rules: dict = {}
    for item in raw:
        if "=" not in item:
            print(f"error: invalid rule '{item}' — expected OLD=NEW", file=sys.stderr)
            sys.exit(1)
        old, new = item.split("=", 1)
        rules[old.strip()] = new.strip()
    return rules


def run_rename(args: argparse.Namespace) -> int:
    try:
        env = load_from_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1

    rules = _parse_rules(args.rules)
    if not rules:
        print("error: at least one --rule OLD=NEW is required", file=sys.stderr)
        return 1

    rm = make_rename_map(rules)
    try:
        renamed = rename_env(env, rm, ignore_missing=not args.strict)
    except KeyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.fmt == "dotenv":
        for key, value in sorted(renamed.items()):
            print(f"{key}={value}")
    else:
        for key in sorted(renamed):
            print(key)

    return 0
