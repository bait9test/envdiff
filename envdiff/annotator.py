"""Annotate environment variable keys with inline comments or metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Annotation:
    key: str
    comment: str
    tags: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        parts = [f"# {self.comment}"]
        if self.tags:
            parts.append(f"# tags: {', '.join(sorted(self.tags))}")
        return "\n".join(parts)


AnnotationMap = Dict[str, Annotation]


def annotate(key: str, comment: str, tags: Optional[List[str]] = None) -> Annotation:
    """Create a single annotation for a key."""
    return Annotation(key=key, comment=comment, tags=list(tags or []))


def build_annotation_map(annotations: List[Annotation]) -> AnnotationMap:
    """Index annotations by key."""
    return {a.key: a for a in annotations}


def annotate_env(env: Dict[str, str], annotation_map: AnnotationMap) -> Dict[str, str]:
    """Return a copy of env keeping only keys that have annotations."""
    return {k: v for k, v in env.items() if k in annotation_map}


def format_annotated_dotenv(
    env: Dict[str, str],
    annotation_map: AnnotationMap,
    include_unannotated: bool = True,
) -> str:
    """Render env as a .env string with inline annotation comments."""
    lines: List[str] = []
    for key, value in env.items():
        annotation = annotation_map.get(key)
        if annotation:
            lines.append(str(annotation))
        elif not include_unannotated:
            continue
        lines.append(f"{key}={value}")
        lines.append("")
    return "\n".join(lines).strip()
