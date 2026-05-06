"""CLI subcommand: group — display env keys organised by prefix or rules."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from envdiff.grouper import group_by_prefix, group_by_rules
from envdiff.loader import load_from_file


def add_group_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "group",
        help="Group environment variables by prefix or custom rules.",
    )
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--sep",
        default="_",
        help="Separator used to detect prefix (default: '_')",
    )
    p.add_argument(
        "--min-size",
        type=int,
        default=1,
        dest="min_size",
        help="Minimum keys for a prefix to form its own group (default: 1)",
    )
    p.add_argument(
        "--rule",
        action="append",
        dest="rules",
        metavar="NAME:PREFIX",
        help="Custom rule in NAME:PREFIX format (repeatable)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--ungrouped-label",
        default="OTHER",
        dest="ungrouped_label",
        help="Label for the catch-all group (default: OTHER)",
    )
    p.set_defaults(func=run_group)


def _parse_rules(raw: Optional[List[str]]) -> dict[str, list[str]]:
    """Parse ``NAME:PREFIX`` strings into a rules dict."""
    result: dict[str, list[str]] = {}
    for entry in raw or []:
        if ":" not in entry:
            print(f"[group] ignoring malformed rule (no ':'): {entry!r}", file=sys.stderr)
            continue
        name, prefix = entry.split(":", 1)
        result.setdefault(name.strip(), []).append(prefix.strip())
    return result


def run_group(args: argparse.Namespace) -> int:
    try:
        env = load_from_file(args.file)
    except FileNotFoundError:
        print(f"[group] file not found: {args.file}", file=sys.stderr)
        return 1

    rules = _parse_rules(args.rules)
    if rules:
        groups = group_by_rules(env, rules, ungrouped_label=args.ungrouped_label)
    else:
        groups = group_by_prefix(
            env,
            sep=args.sep,
            min_group_size=args.min_size,
            ungrouped_label=args.ungrouped_label,
        )

    if args.fmt == "json":
        payload = {name: grp.as_dict() for name, grp in sorted(groups.items())}
        print(json.dumps(payload, indent=2))
    else:
        for name, grp in sorted(groups.items()):
            print(f"[{name}] ({len(grp)} keys)")
            for key in sorted(grp.keys):
                print(f"  {key}")

    return 0
