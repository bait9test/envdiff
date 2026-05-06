"""Tag environment variables with user-defined labels for grouping and annotation."""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Set


@dataclass
class TagMap:
    """Holds a mapping from tag names to sets of matching keys."""

    _data: Dict[str, Set[str]] = field(default_factory=dict)

    def add(self, tag: str, key: str) -> None:
        self._data.setdefault(tag, set()).add(key)

    def tags_for(self, key: str) -> List[str]:
        return sorted(tag for tag, keys in self._data.items() if key in keys)

    def keys_for(self, tag: str) -> Set[str]:
        return set(self._data.get(tag, set()))

    def all_tags(self) -> List[str]:
        return sorted(self._data.keys())

    def as_dict(self) -> Dict[str, List[str]]:
        return {tag: sorted(keys) for tag, keys in self._data.items()}


def tag_by_prefix(env: Dict[str, str], prefix_tag_map: Dict[str, str]) -> TagMap:
    """Auto-tag keys based on their prefix.

    prefix_tag_map: {"AWS_": "aws", "DB_": "database"}
    """
    tm = TagMap()
    for key in env:
        for prefix, tag in prefix_tag_map.items():
            if key.startswith(prefix):
                tm.add(tag, key)
    return tm


def tag_by_pattern(env: Dict[str, str], pattern_tag_map: Dict[str, str]) -> TagMap:
    """Auto-tag keys using glob patterns.

    pattern_tag_map: {"*SECRET*": "sensitive", "*URL*": "network"}
    """
    tm = TagMap()
    for key in env:
        for pattern, tag in pattern_tag_map.items():
            if fnmatch(key, pattern):
                tm.add(tag, key)
    return tm


def merge_tag_maps(*maps: TagMap) -> TagMap:
    """Merge multiple TagMaps into one."""
    merged = TagMap()
    for tm in maps:
        for tag, keys in tm._data.items():
            for key in keys:
                merged.add(tag, key)
    return merged


def filter_env_by_tag(env: Dict[str, str], tag_map: TagMap, tag: str) -> Dict[str, str]:
    """Return only the env keys that carry the given tag."""
    tagged_keys = tag_map.keys_for(tag)
    return {k: v for k, v in env.items() if k in tagged_keys}
