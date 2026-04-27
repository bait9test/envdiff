"""Command-line interface for envdiff."""

import argparse
import sys

from envdiff.loader import load_from_file, load_from_process, load_current_process
from envdiff.differ import diff_envs
from envdiff.formatter import format_diff


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare environment variable sets across .env files or processes.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # files subcommand
    files_cmd = subparsers.add_parser("files", help="Compare two .env files.")
    files_cmd.add_argument("left", help="First .env file")
    files_cmd.add_argument("right", help="Second .env file")
    files_cmd.add_argument("--left-label", default=None, help="Label for the left side")
    files_cmd.add_argument("--right-label", default=None, help="Label for the right side")
    files_cmd.add_argument("--no-color", action="store_true", help="Disable colored output")

    # process subcommand
    proc_cmd = subparsers.add_parser("process", help="Compare a .env file against a running process.")
    proc_cmd.add_argument("file", help="The .env file to compare")
    proc_cmd.add_argument("pid", type=int, help="PID of the running process")
    proc_cmd.add_argument("--left-label", default=None)
    proc_cmd.add_argument("--right-label", default=None)
    proc_cmd.add_argument("--no-color", action="store_true")

    # current subcommand
    cur_cmd = subparsers.add_parser("current", help="Compare a .env file against the current process.")
    cur_cmd.add_argument("file", help="The .env file to compare")
    cur_cmd.add_argument("--left-label", default=None)
    cur_cmd.add_argument("--right-label", default=None)
    cur_cmd.add_argument("--no-color", action="store_true")

    return parser


def run(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    color = not args.no_color

    try:
        if args.command == "files":
            left = load_from_file(args.left)
            right = load_from_file(args.right)
            left_label = args.left_label or args.left
            right_label = args.right_label or args.right

        elif args.command == "process":
            left = load_from_file(args.file)
            right = load_from_process(args.pid)
            left_label = args.left_label or args.file
            right_label = args.right_label or f"pid:{args.pid}"

        elif args.command == "current":
            left = load_from_file(args.file)
            right = load_current_process()
            left_label = args.left_label or args.file
            right_label = args.right_label or "current process"

    except (FileNotFoundError, IsADirectoryError, PermissionError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = diff_envs(left, right)
    output = format_diff(result, left_label=left_label, right_label=right_label, color=color)
    print(output)
    return 1 if result.has_differences() else 0


def main():
    sys.exit(run())


if __name__ == "__main__":
    main()
