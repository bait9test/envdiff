"""CLI subcommand: envdiff stats — show numeric diff statistics."""
from __future__ import annotations

import argparse
import json
import sys

from envdiff.loader import load_from_file
from envdiff.differ import diff_envs
from envdiff.differ_stats import compute_stats, format_stats


def add_stats_subcommand(subparsers: argparse.Action) -> None:
    p = subparsers.add_parser(
        "stats",
        help="Show numeric statistics for a diff between two .env files.",
    )
    p.add_argument("left", help="First .env file")
    p.add_argument("right", help="Second .env file")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colour output",
    )
    p.set_defaults(func=run_stats)


def run_stats(args: argparse.Namespace) -> int:
    try:
        left_env = load_from_file(args.left)
        right_env = load_from_file(args.right)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = diff_envs(left_env, right_env)
    stats = compute_stats(result)

    if args.fmt == "json":
        print(json.dumps(stats.as_dict(), indent=2))
    else:
        print(format_stats(stats, color=not args.no_color))

    return 0
