"""Integration tests: loader.load_snapshot_as_env bridges loader and snapshot."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.loader import load_snapshot_as_env
from envdiff.snapshot import save_snapshot


@pytest.fixture()
def sample_env():
    return {"REDIS_URL": "redis://localhost", "DEBUG": "true"}


def test_load_snapshot_as_env_roundtrip(tmp_path, sample_env):
    snap = tmp_path / "env.snap.json"
    save_snapshot(sample_env, snap)
    loaded = load_snapshot_as_env(snap)
    assert loaded == sample_env


def test_load_snapshot_as_env_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_snapshot_as_env(tmp_path / "missing.json")


def test_load_snapshot_as_env_bad_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{{broken")
    with pytest.raises(ValueError):
        load_snapshot_as_env(bad)


def test_load_snapshot_as_env_returns_strings(tmp_path):
    snap = tmp_path / "typed.json"
    # Manually craft a snapshot where values might be non-string in JSON
    payload = {
        "version": 1,
        "created_at": "2024-01-01T00:00:00+00:00",
        "label": "test",
        "source": "manual",
        "env": {"PORT": 8080, "WORKERS": 4},
    }
    snap.write_text(json.dumps(payload))
    loaded = load_snapshot_as_env(snap)
    assert loaded["PORT"] == "8080"
    assert loaded["WORKERS"] == "4"
    assert all(isinstance(v, str) for v in loaded.values())


def test_load_snapshot_as_env_empty_env(tmp_path):
    snap = tmp_path / "empty.json"
    save_snapshot({}, snap)
    loaded = load_snapshot_as_env(snap)
    assert loaded == {}
