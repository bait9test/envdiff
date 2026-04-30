"""Watch .env files for changes and report diffs automatically."""

import time
import os
from typing import Callable, Optional

from envdiff.loader import load_from_file
from envdiff.differ import diff_envs, DiffResult


def _mtime(path: str) -> float:
    """Return file modification time, or 0.0 if file doesn't exist."""
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0.0


def watch_file(
    path: str,
    callback: Callable[[DiffResult], None],
    interval: float = 1.0,
    max_cycles: Optional[int] = None,
) -> None:
    """
    Poll a .env file for changes and invoke callback with a DiffResult
    whenever the contents change.

    Args:
        path: Path to the .env file to watch.
        callback: Called with a DiffResult when a change is detected.
        interval: Polling interval in seconds.
        max_cycles: Stop after this many poll cycles (useful for testing).
    """
    last_mtime = _mtime(path)
    try:
        previous = load_from_file(path)
    except (FileNotFoundError, IsADirectoryError):
        previous = {}

    cycles = 0
    while True:
        time.sleep(interval)
        cycles += 1

        current_mtime = _mtime(path)
        if current_mtime != last_mtime:
            last_mtime = current_mtime
            try:
                current = load_from_file(path)
            except (FileNotFoundError, IsADirectoryError):
                current = {}

            result = diff_envs(previous, current)
            callback(result)
            previous = current

        if max_cycles is not None and cycles >= max_cycles:
            break


def watch_two_files(
    path_a: str,
    path_b: str,
    callback: Callable[[DiffResult], None],
    interval: float = 1.0,
    max_cycles: Optional[int] = None,
) -> None:
    """
    Poll two .env files and invoke callback with a DiffResult whenever
    either file changes.
    """
    last_mtime_a = _mtime(path_a)
    last_mtime_b = _mtime(path_b)

    def _load(p: str) -> dict:
        try:
            return load_from_file(p)
        except (FileNotFoundError, IsADirectoryError):
            return {}

    env_a = _load(path_a)
    env_b = _load(path_b)

    cycles = 0
    while True:
        time.sleep(interval)
        cycles += 1

        mtime_a = _mtime(path_a)
        mtime_b = _mtime(path_b)
        changed = mtime_a != last_mtime_a or mtime_b != last_mtime_b

        if changed:
            last_mtime_a, last_mtime_b = mtime_a, mtime_b
            env_a = _load(path_a)
            env_b = _load(path_b)
            callback(diff_envs(env_a, env_b))

        if max_cycles is not None and cycles >= max_cycles:
            break
