"""CLI subcommand: envdiff inspect — inspect a key across multiple .env files."""

from __future__ import annotations

import json
import sys
from argparse import ArgumentParser, Namespace
from typing import List

from envdiff.inspector import inspect_all, inspect_key
from envdiff.loader import load_from_file


def add_inspect_subcommand(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "inspect",
        help="Inspect one or more keys across multiple .env files",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help=".env files to inspect")
    p.add_argument(
        "--key", "-k",
        dest="keys",
        action="append",
        default=[],
        metavar="KEY",
        help="Key(s) to inspect (omit to inspect all keys)",
    )
    p.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        dest="fmt",
    )
    p.add_argument(
        "--labels",
        nargs="+",
        default=[],
        metavar="LABEL",
        help="Labels for each file (must match number of files)",
    )
    p.set_defaults(func=run_inspect)


def run_inspect(args: Namespace) -> int:
    labels: List[str] = args.labels or args.files
    if len(labels) != len(args.files):
        print("error: number of labels must match number of files", file=sys.stderr)
        return 2

    envs = {}
    for label, path in zip(labels, args.files):
        try:
            envs[label] = load_from_file(path)
        except (FileNotFoundError, IsADirectoryError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    if args.keys:
        inspections = [inspect_key(k, envs) for k in args.keys]
    else:
        inspections = inspect_all(envs)

    if args.fmt == "json":
        print(json.dumps([i.as_dict() for i in inspections], indent=2))
        return 0

    # text output
    for insp in inspections:
        status = "OK" if insp.is_consistent else "DRIFT"
        print(f"[{status}] {insp.key}")
        for src, val in insp.sources.items():
            display = val if val is not None else "<missing>"
            typ = insp.inferred_types[src]
            print(f"  {src}: {display!r}  ({typ})")
        if not insp.type_consistent:
            print("  ! type mismatch across sources")
    return 0
