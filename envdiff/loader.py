"""Loader module for reading env variables from files or running processes."""

import os
import subprocess
from pathlib import Path
from typing import Dict, Optional

from envdiff.parser import parse_env_file, parse_env_string


def load_from_file(path: str) -> Dict[str, str]:
    """Load environment variables from a .env file.

    Args:
        path: Path to the .env file.

    Returns:
        Dictionary of environment variable key-value pairs.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If the file cannot be read.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"env file not found: {path}")
    if not file_path.is_file():
        raise IOError(f"path is not a file: {path}")
    return parse_env_file(str(file_path))


def load_from_process(pid: int) -> Dict[str, str]:
    """Load environment variables from a running process by PID.

    Reads from /proc/<pid>/environ on Linux systems.

    Args:
        pid: Process ID of the target process.

    Returns:
        Dictionary of environment variable key-value pairs.

    Raises:
        FileNotFoundError: If the process or its environ file is not found.
        PermissionError: If access to the process environ is denied.
    """
    environ_path = Path(f"/proc/{pid}/environ")
    if not environ_path.exists():
        raise FileNotFoundError(f"no such process or /proc not available: pid={pid}")
    try:
        raw = environ_path.read_bytes()
    except PermissionError:
        raise PermissionError(f"permission denied reading environ for pid={pid}")

    env: Dict[str, str] = {}
    for entry in raw.split(b"\x00"):
        if b"=" in entry:
            key, _, value = entry.partition(b"=")
            env[key.decode(errors="replace")] = value.decode(errors="replace")
    return env


def load_current_process() -> Dict[str, str]:
    """Load environment variables from the current process.

    Returns:
        Dictionary of environment variable key-value pairs.
    """
    return dict(os.environ)


def load_from_string(text: str) -> Dict[str, str]:
    """Load environment variables from a raw env-format string.

    Args:
        text: Multi-line string in .env format.

    Returns:
        Dictionary of environment variable key-value pairs.
    """
    return parse_env_string(text)
