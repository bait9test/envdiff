"""Normalize environment variable keys and values for comparison."""

from __future__ import annotations

import re
from typing import Dict


def normalize_key(key: str, *, uppercase: bool = True, strip: bool = True) -> str:
    """Normalize a single env key."""
    if strip:
        key = key.strip()
    if uppercase:
        key = key.upper()
    return key


def normalize_value(value: str, *, strip: bool = True, collapse_whitespace: bool = False) -> str:
    """Normalize a single env value."""
    if strip:
        value = value.strip()
    if collapse_whitespace:
        value = re.sub(r"\s+", " ", value)
    return value


def normalize_env(
    env: Dict[str, str],
    *,
    uppercase_keys: bool = True,
    strip_keys: bool = True,
    strip_values: bool = True,
    collapse_whitespace: bool = False,
) -> Dict[str, str]:
    """Return a new dict with normalized keys and values.

    If two keys collide after normalization the last one (in iteration order) wins.
    """
    result: Dict[str, str] = {}
    for key, value in env.items():
        nk = normalize_key(key, uppercase=uppercase_keys, strip=strip_keys)
        nv = normalize_value(value, strip=strip_values, collapse_whitespace=collapse_whitespace)
        result[nk] = nv
    return result


def normalize_pair(
    left: Dict[str, str],
    right: Dict[str, str],
    **kwargs,
) -> tuple[Dict[str, str], Dict[str, str]]:
    """Normalize two env dicts with the same settings."""
    return normalize_env(left, **kwargs), normalize_env(right, **kwargs)
