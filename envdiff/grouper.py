"""Group environment variables by shared prefix or custom rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EnvGroup:
    """A named collection of environment variable keys."""

    name: str
    keys: List[str] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.keys)

    def __contains__(self, key: str) -> bool:
        return key in self.keys

    def as_dict(self) -> Dict[str, object]:
        return {"name": self.name, "keys": sorted(self.keys), "count": len(self.keys)}


def group_by_prefix(
    env: Dict[str, str],
    *,
    sep: str = "_",
    min_group_size: int = 1,
    ungrouped_label: str = "OTHER",
) -> Dict[str, EnvGroup]:
    """Partition *env* keys into groups by their first prefix segment.

    Keys that share the same token before the first *sep* are placed together.
    Keys without *sep* land in the *ungrouped_label* bucket.
    Groups smaller than *min_group_size* are also folded into that bucket.
    """
    buckets: Dict[str, List[str]] = {}
    for key in env:
        prefix = key.split(sep, 1)[0] if sep in key else ungrouped_label
        buckets.setdefault(prefix, []).append(key)

    groups: Dict[str, EnvGroup] = {}
    ungrouped = EnvGroup(ungrouped_label)

    for prefix, keys in buckets.items():
        if prefix == ungrouped_label or len(keys) < min_group_size:
            ungrouped.keys.extend(keys)
        else:
            groups[prefix] = EnvGroup(name=prefix, keys=list(keys))

    if ungrouped.keys:
        groups[ungrouped_label] = ungrouped

    return groups


def group_by_rules(
    env: Dict[str, str],
    rules: Dict[str, List[str]],
    *,
    ungrouped_label: str = "OTHER",
) -> Dict[str, EnvGroup]:
    """Assign keys to named groups according to explicit prefix *rules*.

    *rules* maps group name -> list of key prefixes that belong to it.
    Keys not matched by any rule land in *ungrouped_label*.
    """
    assigned: set[str] = set()
    groups: Dict[str, EnvGroup] = {}

    for group_name, prefixes in rules.items():
        matched = [
            k for k in env if any(k.startswith(p) for p in prefixes)
        ]
        groups[group_name] = EnvGroup(name=group_name, keys=matched)
        assigned.update(matched)

    leftover = [k for k in env if k not in assigned]
    if leftover:
        groups[ungrouped_label] = EnvGroup(name=ungrouped_label, keys=leftover)

    return groups


def merge_groups(
    *group_maps: Dict[str, EnvGroup],
) -> Dict[str, EnvGroup]:
    """Merge multiple group maps, combining keys for matching group names."""
    merged: Dict[str, EnvGroup] = {}
    for gmap in group_maps:
        for name, grp in gmap.items():
            if name not in merged:
                merged[name] = EnvGroup(name=name)
            merged[name].keys.extend(k for k in grp.keys if k not in merged[name].keys)
    return merged
