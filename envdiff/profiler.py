"""Profile environment variable sets: count keys, detect duplicates across sources, summarize value types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class EnvProfile:
    label: str
    total_keys: int
    empty_values: List[str] = field(default_factory=list)
    numeric_values: List[str] = field(default_factory=list)
    boolean_values: List[str] = field(default_factory=list)
    url_values: List[str] = field(default_factory=list)
    longest_key: str = ""
    longest_value_key: str = ""


def _looks_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def _looks_boolean(value: str) -> bool:
    return value.lower() in {"true", "false", "yes", "no", "1", "0"}


def _looks_url(value: str) -> bool:
    return value.startswith(("http://", "https://", "ftp://"))


def profile_env(env: Dict[str, str], label: str = "env") -> EnvProfile:
    """Build a profile summary for a single env dict."""
    empty: List[str] = []
    numeric: List[str] = []
    boolean: List[str] = []
    urls: List[str] = []

    longest_key = max(env.keys(), key=len, default="")
    longest_value_key = max(env.keys(), key=lambda k: len(env[k]), default="")

    for key, value in env.items():
        if value == "":
            empty.append(key)
        elif _looks_boolean(value):
            boolean.append(key)
        elif _looks_numeric(value):
            numeric.append(key)
        elif _looks_url(value):
            urls.append(key)

    return EnvProfile(
        label=label,
        total_keys=len(env),
        empty_values=empty,
        numeric_values=numeric,
        boolean_values=boolean,
        url_values=urls,
        longest_key=longest_key,
        longest_value_key=longest_value_key,
    )


def compare_profiles(left: EnvProfile, right: EnvProfile) -> List[Tuple[str, str, str]]:
    """Return a list of (metric, left_value, right_value) tuples for display."""
    rows: List[Tuple[str, str, str]] = [
        ("total keys", str(left.total_keys), str(right.total_keys)),
        ("empty values", str(len(left.empty_values)), str(len(right.empty_values))),
        ("numeric values", str(len(left.numeric_values)), str(len(right.numeric_values))),
        ("boolean values", str(len(left.boolean_values)), str(len(right.boolean_values))),
        ("url values", str(len(left.url_values)), str(len(right.url_values))),
        ("longest key", left.longest_key, right.longest_key),
        ("longest value key", left.longest_value_key, right.longest_value_key),
    ]
    return rows
