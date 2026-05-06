"""CLI subcommand: annotate — render a .env file with inline comments."""

from __future__ import annotations

import argparse
import sys
from typing import List

from envdiff.annotator import annotate, build_annotation_map, format_annotated_dotenv
from envdiff.loader import load_from_file


def add_annotate_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("annotate", help="Annotate .env keys with inline comments")
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--rule",
        dest="rules",
        metavar="KEY:COMMENT",
        action="append",
        default=[],
        help="Annotation rule in KEY:COMMENT format (repeatable)",
    )
    p.add_argument(
        "--tag",
        dest="tags",
        metavar="KEY:TAG",
        action="append",
        default=[],
        help="Tag rule in KEY:TAG format (repeatable)",
    )
    p.add_argument(
        "--only-annotated",
        action="store_true",
        default=False,
        help="Omit keys that have no annotation",
    )
    p.set_defaults(func=run_annotate)


def _parse_rules(rules: List[str]) -> dict:  # type: ignore[type-arg]
    result = {}
    for rule in rules:
        if ":" not in rule:
            continue
        key, _, comment = rule.partition(":")
        result[key.strip()] = comment.strip()
    return result


def _parse_tags(tags: List[str]) -> dict:  # type: ignore[type-arg]
    result: dict = {}  # type: ignore[type-arg]
    for tag in tags:
        if ":" not in tag:
            continue
        key, _, tag_value = tag.partition(":")
        result.setdefault(key.strip(), []).append(tag_value.strip())
    return result


def run_annotate(args: argparse.Namespace) -> int:
    try:
        env = load_from_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1

    comments = _parse_rules(args.rules)
    tags_map = _parse_tags(args.tags)

    if not comments:
        print("error: at least one --rule KEY:COMMENT is required", file=sys.stderr)
        return 1

    annotations = [
        annotate(key, comment, tags_map.get(key))
        for key, comment in comments.items()
    ]
    amap = build_annotation_map(annotations)
    output = format_annotated_dotenv(env, amap, include_unannotated=not args.only_annotated)
    print(output)
    return 0
