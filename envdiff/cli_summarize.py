"""CLI sub-command: summarize — print a concise diff summary."""

from __future__ import annotations

import argparse
import json
import sys

from envdiff.loader import load_from_file
from envdiff.differ import diff_envs
from envdiff.summarizer import summarize, format_summary


def add_summarize_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "summarize",
        help="Print a concise summary of differences between two .env files.",
    )
    p.add_argument("file_a", help="First .env file")
    p.add_argument("file_b", help="Second .env file")
    p.add_argument(
        "--label-left", default="left", metavar="LABEL",
        help="Label for the first file (default: left)",
    )
    p.add_argument(
        "--label-right", default="right", metavar="LABEL",
        help="Label for the second file (default: right)",
    )
    p.add_argument(
        "--json", dest="as_json", action="store_true",
        help="Output summary as JSON",
    )
    p.set_defaults(func=run_summarize)


def run_summarize(args: argparse.Namespace) -> int:
    try:
        env_a = load_from_file(args.file_a)
        env_b = load_from_file(args.file_b)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = diff_envs(env_a, env_b)
    s = summarize(result, label_left=args.label_left, label_right=args.label_right)

    if args.as_json:
        print(json.dumps(s.as_dict(), indent=2))
    else:
        print(format_summary(s, label_left=args.label_left, label_right=args.label_right))

    return 0
