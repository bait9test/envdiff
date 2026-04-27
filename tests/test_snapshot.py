"""Tests for envdiff.snapshot."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.snapshot import (
    SNAPSHOT_VERSION,
    load_snapshot,
    save_snapshot,
    snapshot_metadata,
)


@pytest.fixture()
def env_sample() -> dict:
    return {"APP_ENV": "production", "DB_HOST": "localhost", "PORT": "5432"}


def test_save_creates_file(tmp_path, env_sample):
    out = tmp_path / "snap.json"
    save_snapshot(env_sample, out)
    assert out.exists()


def test_save_contains_all_keys(tmp_path, env_sample):
    out = tmp_path / "snap.json"
    save_snapshot(env_sample, out)
    payload = json.loads(out.read_text())
    assert payload["env"] == env_sample


def test_save_includes_version(tmp_path, env_sample):
    out = tmp_path / "snap.json"
    save_snapshot(env_sample, out)
    payload = json.loads(out.read_text())
    assert payload["version"] == SNAPSHOT_VERSION


def test_save_custom_label(tmp_path, env_sample):
    out = tmp_path / "snap.json"
    save_snapshot(env_sample, out, label="staging")
    payload = json.loads(out.read_text())
    assert payload["label"] == "staging"


def test_save_custom_source(tmp_path, env_sample):
    out = tmp_path / "snap.json"
    save_snapshot(env_sample, out, source="process:1234")
    payload = json.loads(out.read_text())
    assert payload["source"] == "process:1234"


def test_load_roundtrip(tmp_path, env_sample):
    out = tmp_path / "snap.json"
    save_snapshot(env_sample, out)
    loaded = load_snapshot(out)
    assert loaded == env_sample


def test_load_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_snapshot(tmp_path / "nope.json")


def test_load_invalid_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_snapshot(bad)


def test_load_missing_env_key(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"version": 1}))
    with pytest.raises(ValueError, match="envdiff snapshot"):
        load_snapshot(bad)


def test_metadata_key_count(tmp_path, env_sample):
    out = tmp_path / "snap.json"
    save_snapshot(env_sample, out, label="prod")
    meta = snapshot_metadata(out)
    assert meta["key_count"] == len(env_sample)
    assert meta["label"] == "prod"


def test_metadata_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        snapshot_metadata(tmp_path / "ghost.json")
