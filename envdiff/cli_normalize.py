"""CLI subcommand: normalize — print a normalized version of an env file."""

from __future__ import annotations

import argparse
import sys

from envdiff.loader import load_from_file
from envdiff.normalizer import normalize_env


def add_normalize_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "normalize",
        help="Print a normalized .env file to stdout.",
    )
    p.add_argument("file", help="Path to the .env file to normalize.")
    p.add_argument(
        "--no-uppercase",
        dest="uppercase",
        action="store_false",
        default=True,
        help="Do not uppercase keys.",
    )
    p.add_argument(
        "--collapse-whitespace",
        action="store_true",
        default=False,
        help="Collapse internal whitespace in values.",
    )
    p.add_argument(
        "--format",
        choices=["dotenv", "keys"],
        default="dotenv",
        help="Output format (default: dotenv).",
    )
    p.set_defaults(func=run_normalize)


def run_normalize(args: argparse.Namespace) -> int:
    try:
        env = load_from_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    except IsADirectoryError:
        print(f"error: path is a directory: {args.file}", file=sys.stderr)
        return 1

    normalized = normalize_env(
        env,
        uppercase_keys=args.uppercase,
        collapse_whitespace=args.collapse_whitespace,
    )

    if args.format == "dotenv":
        for key, value in sorted(normalized.items()):
            print(f"{key}={value}")
    else:
        for key in sorted(normalized.keys()):
            print(key)

    return 0
