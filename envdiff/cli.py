"""CLI entry point for envdiff."""

from __future__ import annotations

import argparse
import sys

from envdiff.differ import diff_envs
from envdiff.formatter import format_diff
from envdiff.loader import load_from_file, load_from_process
from envdiff.reporter import report, ReportFormat


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare environment variable sets.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- files subcommand ---
    files_cmd = subparsers.add_parser("files", help="Compare two .env files.")
    files_cmd.add_argument("left", help="First .env file.")
    files_cmd.add_argument("right", help="Second .env file.")
    files_cmd.add_argument("--no-color", action="store_true", help="Disable colored output.")
    files_cmd.add_argument("--labels", nargs=2, metavar=("LEFT", "RIGHT"), default=None)
    files_cmd.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        dest="fmt",
        help="Output format (default: text).",
    )

    # --- process subcommand ---
    proc_cmd = subparsers.add_parser("process", help="Compare env of a running process with a .env file.")
    proc_cmd.add_argument("pid", type=int, help="PID of the process to inspect.")
    proc_cmd.add_argument("file", help=".env file to compare against.")
    proc_cmd.add_argument("--no-color", action="store_true", help="Disable colored output.")
    proc_cmd.add_argument("--labels", nargs=2, metavar=("LEFT", "RIGHT"), default=None)
    proc_cmd.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        dest="fmt",
    )

    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "files":
        try:
            left_env = load_from_file(args.left)
            right_env = load_from_file(args.right)
        except (FileNotFoundError, IsADirectoryError) as exc:
            print(f"envdiff: error: {exc}", file=sys.stderr)
            return 1
        labels = tuple(args.labels) if args.labels else (args.left, args.right)

    elif args.command == "process":
        try:
            left_env = load_from_process(args.pid)
            right_env = load_from_file(args.file)
        except (FileNotFoundError, IsADirectoryError, PermissionError, ProcessLookupError) as exc:
            print(f"envdiff: error: {exc}", file=sys.stderr)
            return 1
        labels = tuple(args.labels) if args.labels else (f"pid:{args.pid}", args.file)
    else:
        return 1

    result = diff_envs(left_env, right_env)
    fmt: ReportFormat = args.fmt

    if fmt == "text" and not getattr(args, "no_color", False):
        print(format_diff(result, labels=labels, color=not args.no_color))
    else:
        print(report(result, fmt=fmt, labels=labels))

    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
