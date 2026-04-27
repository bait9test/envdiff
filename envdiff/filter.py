"""Filter environment variable keys by prefix, pattern, or explicit list."""

from __future__ import annotations

import fnmatch
import re
from typing import Dict, List, Optional


def filter_by_prefix(
    env: Dict[str, str], prefixes: List[str]
) -> Dict[str, str]:
    """Return only keys that start with any of the given prefixes."""
    if not prefixes:
        return env
    return {
        k: v
        for k, v in env.items()
        if any(k.startswith(p) for p in prefixes)
    }


def filter_by_pattern(
    env: Dict[str, str], pattern: str
) -> Dict[str, str]:
    """Return only keys matching a glob-style pattern (e.g. 'DB_*')."""
    return {k: v for k, v in env.items() if fnmatch.fnmatch(k, pattern)}


def filter_by_regex(
    env: Dict[str, str], regex: str
) -> Dict[str, str]:
    """Return only keys matching the given regular expression."""
    compiled = re.compile(regex)
    return {k: v for k, v in env.items() if compiled.search(k)}


def exclude_keys(
    env: Dict[str, str], keys: List[str]
) -> Dict[str, str]:
    """Return env dict with the specified keys removed."""
    excluded = set(keys)
    return {k: v for k, v in env.items() if k not in excluded}


def apply_filters(
    env: Dict[str, str],
    *,
    prefixes: Optional[List[str]] = None,
    pattern: Optional[str] = None,
    regex: Optional[str] = None,
    exclude: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Apply all requested filters in sequence and return the result."""
    result = dict(env)
    if prefixes:
        result = filter_by_prefix(result, prefixes)
    if pattern:
        result = filter_by_pattern(result, pattern)
    if regex:
        result = filter_by_regex(result, regex)
    if exclude:
        result = exclude_keys(result, exclude)
    return result
