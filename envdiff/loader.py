"""Loaders: read environment variables from files, processes, or strings."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

from envdiff.parser import parse_env_file, parse_env_string


def load_from_file(path: str | Path) -> Dict[str, str]:
    """Parse a .env file and return a dict of key/value pairs.

    Raises:
        FileNotFoundError: if *path* does not exist.
        IsADirectoryError: if *path* is a directory.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"Expected a file, got a directory: {path}")
    return parse_env_file(path)


def load_from_process(pid: int) -> Dict[str, str]:
    """Read environment variables from a running process by PID (Linux/macOS).

    Raises:
        FileNotFoundError: if the process does not exist.
        PermissionError: if access to the process environment is denied.
    """
    env_file = Path(f"/proc/{pid}/environ")
    if not env_file.exists():
        raise FileNotFoundError(f"No such process: {pid}")
    try:
        raw = env_file.read_bytes()
    except PermissionError as exc:
        raise PermissionError(
            f"Permission denied reading environment of process {pid}"
        ) from exc
    pairs = raw.split(b"\x00")
    result: Dict[str, str] = {}
    for pair in pairs:
        decoded = pair.decode("utf-8", errors="replace")
        if "=" in decoded:
            key, _, value = decoded.partition("=")
            result[key] = value
    return result


def load_current_process() -> Dict[str, str]:
    """Return a copy of the current process environment."""
    return dict(os.environ)


def load_from_string(text: str) -> Dict[str, str]:
    """Parse a multi-line .env-formatted string and return key/value pairs."""
    return parse_env_string(text)


def load_snapshot_as_env(path: str | Path) -> Dict[str, str]:
    """Load an envdiff snapshot file and return the stored environment dict.

    This is a thin convenience wrapper around :func:`envdiff.snapshot.load_snapshot`
    so callers can use a unified ``load_*`` interface.

    Raises:
        FileNotFoundError: if *path* does not exist.
        ValueError: if the file is not a valid snapshot.
    """
    from envdiff.snapshot import load_snapshot  # local import to avoid cycles

    return load_snapshot(path)
