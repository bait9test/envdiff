"""CLI subcommand: score — show similarity score between two .env files."""

import argparse
import sys

from envdiff.loader import load_from_file
from envdiff.scorer import score_envs


def add_score_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "score",
        help="Show a similarity score between two .env files.",
    )
    p.add_argument("file_a", help="First .env file")
    p.add_argument("file_b", help="Second .env file")
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output score as JSON.",
    )
    p.set_defaults(func=run_score)


def run_score(args: argparse.Namespace) -> int:
    try:
        left = load_from_file(args.file_a)
        right = load_from_file(args.file_b)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    s = score_envs(left, right)

    if args.json:
        import json
        print(json.dumps({
            "score": s.score,
            "percent": s.as_percent(),
            "grade": s.grade(),
            "total_keys": s.total_keys,
            "matching_keys": s.matching_keys,
            "changed_keys": s.changed_keys,
            "only_in_left": s.only_in_left,
            "only_in_right": s.only_in_right,
        }))
    else:
        print(f"Similarity : {s.as_percent()}  (grade {s.grade()}"  ")")
        print(f"Total keys : {s.total_keys}")
        print(f"Matching   : {s.matching_keys}")
        print(f"Changed    : {s.changed_keys}")
        print(f"Only left  : {s.only_in_left}")
        print(f"Only right : {s.only_in_right}")

    return 0
