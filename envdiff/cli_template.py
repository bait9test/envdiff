"""CLI subcommand: generate an env template from a file or diff."""

from __future__ import annotations

import argparse
import sys

from envdiff.loader import load_from_file
from envdiff.differ import diff_envs
from envdiff.templater import TemplateOptions, diff_to_template, env_to_template, write_template


def add_template_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "template",
        help="Generate a .env template from one or two env files",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help="One or two .env files")
    p.add_argument(
        "--placeholder",
        default="<FILL_ME>",
        help="Placeholder value for keys (default: <FILL_ME>)",
    )
    p.add_argument(
        "--include-values",
        action="store_true",
        default=False,
        help="Preserve actual values instead of placeholder",
    )
    p.add_argument(
        "--no-comments",
        action="store_true",
        default=False,
        help="Omit annotation comments in diff mode",
    )
    p.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write output to FILE instead of stdout",
    )
    p.set_defaults(func=run_template)


def run_template(args: argparse.Namespace) -> int:
    opts = TemplateOptions(
        placeholder=args.placeholder,
        include_values=args.include_values,
        include_comments=not args.no_comments,
    )

    if len(args.files) == 1:
        env = load_from_file(args.files[0])
        content = env_to_template(env, opts)
    elif len(args.files) == 2:
        left = load_from_file(args.files[0])
        right = load_from_file(args.files[1])
        result = diff_envs(left, right)
        content = diff_to_template(result, opts)
    else:
        print("error: provide one or two env files", file=sys.stderr)
        return 1

    if args.output:
        write_template(args.output, content)
    else:
        sys.stdout.write(content)

    return 0
