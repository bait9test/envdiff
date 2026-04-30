"""CLI helpers for the 'merge' subcommand."""

import sys
from typing import List, Optional

from envdiff.loader import load_from_file
from envdiff.merger import MergeConflictError, MergeStrategy, merge_envs, merge_origins


def add_merge_subcommand(subparsers) -> None:
    """Register the 'merge' subcommand onto an existing subparsers action."""
    p = subparsers.add_parser(
        "merge",
        help="Merge multiple .env files into one",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help=".env files to merge")
    p.add_argument(
        "--strategy",
        choices=[s.value for s in MergeStrategy],
        default=MergeStrategy.LAST.value,
        help="Conflict resolution strategy (default: last)",
    )
    p.add_argument(
        "--output", "-o",
        metavar="FILE",
        default=None,
        help="Write merged result to FILE instead of stdout",
    )
    p.add_argument(
        "--show-origins",
        action="store_true",
        help="Print which file each key came from",
    )
    p.set_defaults(func=run_merge)


def run_merge(args) -> int:
    """Execute the merge subcommand. Returns exit code."""
    envs = []
    labels: List[str] = []

    for path in args.files:
        try:
            envs.append(load_from_file(path))
            labels.append(path)
        except (FileNotFoundError, IsADirectoryError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    strategy = MergeStrategy(args.strategy)

    try:
        merged = merge_envs(envs, strategy=strategy, labels=labels)
    except MergeConflictError as exc:
        print(f"merge conflict: {exc}", file=sys.stderr)
        return 2

    lines = [f"{k}={v}" for k, v in sorted(merged.items())]
    output = "\n".join(lines) + ("\n" if lines else "")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output)
    else:
        sys.stdout.write(output)

    if getattr(args, "show_origins", False):
        origins = merge_origins(envs, labels=labels)
        print("\n# Origins:", file=sys.stderr)
        for key in sorted(origins):
            sources = ", ".join(origins[key])
            print(f"#  {key}: {sources}", file=sys.stderr)

    return 0
