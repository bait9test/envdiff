"""CLI subcommand: tag — auto-tag env keys by prefix or pattern."""

from __future__ import annotations

import argparse
import json
import sys

from envdiff.loader import load_from_file
from envdiff.tagger import tag_by_pattern, tag_by_prefix, merge_tag_maps


def add_tag_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("tag", help="Auto-tag env keys by prefix or glob pattern")
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--prefix",
        nargs=2,
        metavar=("PREFIX", "TAG"),
        action="append",
        default=[],
        dest="prefixes",
        help="Map a key prefix to a tag (repeatable)",
    )
    p.add_argument(
        "--pattern",
        nargs=2,
        metavar=("GLOB", "TAG"),
        action="append",
        default=[],
        dest="patterns",
        help="Map a glob pattern to a tag (repeatable)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    p.set_defaults(func=run_tag)


def run_tag(args: argparse.Namespace) -> int:
    env = load_from_file(args.file)

    prefix_map = {prefix: tag for prefix, tag in args.prefixes}
    pattern_map = {pat: tag for pat, tag in args.patterns}

    maps = []
    if prefix_map:
        maps.append(tag_by_prefix(env, prefix_map))
    if pattern_map:
        maps.append(tag_by_pattern(env, pattern_map))

    if not maps:
        print("No --prefix or --pattern rules provided.", file=sys.stderr)
        return 1

    merged = merge_tag_maps(*maps)

    if args.fmt == "json":
        print(json.dumps(merged.as_dict(), indent=2))
    else:
        for tag in merged.all_tags():
            keys = sorted(merged.keys_for(tag))
            print(f"[{tag}]")
            for k in keys:
                print(f"  {k}")

    return 0
