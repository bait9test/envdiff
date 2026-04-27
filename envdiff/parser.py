"""Parser for .env files — handles reading and parsing key-value pairs."""

import re
from pathlib import Path
from typing import Dict, Optional


ENV_LINE_RE = re.compile(
    r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$"
)
COMMENT_RE = re.compile(r"^\s*#")


def parse_env_file(path: str | Path) -> Dict[str, str]:
    """Parse a .env file and return a dict of key-value pairs.

    - Ignores blank lines and comments (lines starting with #)
    - Strips surrounding quotes from values (single or double)
    - Raises FileNotFoundError if the file doesn't exist
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"env file not found: {path}")

    env: Dict[str, str] = {}

    with path.open("r", encoding="utf-8") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line = raw_line.rstrip("\n")

            # skip blanks and comments
            if not line.strip() or COMMENT_RE.match(line):
                continue

            match = ENV_LINE_RE.match(line)
            if not match:
                # silently skip malformed lines (could log a warning here)
                continue

            key = match.group("key")
            value = _strip_quotes(match.group("value").strip())
            env[key] = value

    return env


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value string."""
    if len(value) >= 2:
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            return value[1:-1]
    return value


def parse_env_string(content: str) -> Dict[str, str]:
    """Parse env content from a raw string — useful for testing or piped input."""
    env: Dict[str, str] = {}
    for line in content.splitlines():
        if not line.strip() or COMMENT_RE.match(line):
            continue
        match = ENV_LINE_RE.match(line)
        if match:
            env[match.group("key")] = _strip_quotes(match.group("value").strip())
    return env
