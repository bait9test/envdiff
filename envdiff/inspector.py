"""Inspect individual keys across env sets — type hints, presence, and value drift."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.profiler import _looks_boolean, _looks_numeric, _looks_url


@dataclass
class KeyInspection:
    key: str
    sources: Dict[str, Optional[str]] = field(default_factory=dict)

    @property
    def present_in(self) -> List[str]:
        return [src for src, val in self.sources.items() if val is not None]

    @property
    def missing_from(self) -> List[str]:
        return [src for src, val in self.sources.items() if val is None]

    @property
    def is_consistent(self) -> bool:
        vals = [v for v in self.sources.values() if v is not None]
        return len(set(vals)) <= 1

    @property
    def inferred_types(self) -> Dict[str, str]:
        result = {}
        for src, val in self.sources.items():
            if val is None:
                result[src] = "missing"
            elif _looks_boolean(val):
                result[src] = "boolean"
            elif _looks_numeric(val):
                result[src] = "numeric"
            elif _looks_url(val):
                result[src] = "url"
            else:
                result[src] = "string"
        return result

    @property
    def type_consistent(self) -> bool:
        types = [t for t in self.inferred_types.values() if t != "missing"]
        return len(set(types)) <= 1

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "sources": self.sources,
            "present_in": self.present_in,
            "missing_from": self.missing_from,
            "is_consistent": self.is_consistent,
            "inferred_types": self.inferred_types,
            "type_consistent": self.type_consistent,
        }


def inspect_key(key: str, envs: Dict[str, Dict[str, str]]) -> KeyInspection:
    """Inspect a single key across multiple named env dicts."""
    sources = {label: env.get(key) for label, env in envs.items()}
    return KeyInspection(key=key, sources=sources)


def inspect_all(envs: Dict[str, Dict[str, str]]) -> List[KeyInspection]:
    """Inspect every key that appears in any of the provided envs."""
    all_keys: set = set()
    for env in envs.values():
        all_keys.update(env.keys())
    return [inspect_key(k, envs) for k in sorted(all_keys)]
