"""Snapshot support: save and load environment snapshots to/from JSON files."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


SNAPSHOT_VERSION = 1


def save_snapshot(
    env: Dict[str, str],
    path: str | Path,
    label: Optional[str] = None,
    source: Optional[str] = None,
) -> None:
    """Persist an environment dict as a JSON snapshot file."""
    path = Path(path)
    payload = {
        "version": SNAPSHOT_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "label": label or path.stem,
        "source": source or "unknown",
        "env": env,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def load_snapshot(path: str | Path) -> Dict[str, str]:
    """Load an environment dict from a previously saved snapshot file.

    Raises:
        FileNotFoundError: if *path* does not exist.
        ValueError: if the file is not a valid envdiff snapshot.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot file not found: {path}")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in snapshot file: {path}") from exc

    if not isinstance(payload, dict) or "env" not in payload:
        raise ValueError(
            f"File does not look like an envdiff snapshot: {path}"
        )

    env = payload["env"]
    if not isinstance(env, dict):
        raise ValueError(f"Snapshot 'env' field is not a mapping: {path}")

    return {str(k): str(v) for k, v in env.items()}


def snapshot_metadata(path: str | Path) -> Dict[str, object]:
    """Return metadata fields (version, created_at, label, source) without the env."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot file not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        "version": payload.get("version"),
        "created_at": payload.get("created_at"),
        "label": payload.get("label"),
        "source": payload.get("source"),
        "key_count": len(payload.get("env", {})),
    }
