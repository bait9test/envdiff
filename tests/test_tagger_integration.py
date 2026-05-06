"""Integration tests: tagger + filter_env_by_tag working together."""

from pathlib import Path

import pytest

from envdiff.loader import load_from_file
from envdiff.tagger import tag_by_prefix, tag_by_pattern, merge_tag_maps, filter_env_by_tag
from envdiff.differ import diff_envs


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text(
        "AWS_KEY=abc\n"
        "AWS_SECRET=xyz\n"
        "DB_HOST=prod-db\n"
        "DB_PORT=5432\n"
        "REDIS_URL=redis://localhost\n"
        "LOG_LEVEL=info\n"
    )
    return f


@pytest.fixture
def env_file_b(tmp_path: Path) -> Path:
    f = tmp_path / ".env.staging"
    f.write_text(
        "AWS_KEY=abc\n"
        "AWS_SECRET=staging-secret\n"
        "DB_HOST=staging-db\n"
        "DB_PORT=5432\n"
        "REDIS_URL=redis://staging\n"
        "LOG_LEVEL=debug\n"
    )
    return f


def test_tag_then_filter_returns_subset(env_file):
    env = load_from_file(env_file)
    tm = tag_by_prefix(env, {"AWS_": "aws"})
    aws_env = filter_env_by_tag(env, tm, "aws")
    assert set(aws_env.keys()) == {"AWS_KEY", "AWS_SECRET"}


def test_tag_pattern_covers_multiple_prefixes(env_file):
    env = load_from_file(env_file)
    tm = tag_by_pattern(env, {"*_HOST": "host_keys", "*_PORT": "host_keys"})
    host_keys = filter_env_by_tag(env, tm, "host_keys")
    assert "DB_HOST" in host_keys
    assert "DB_PORT" in host_keys


def test_diff_on_tagged_subset(env_file, env_file_b):
    left = load_from_file(env_file)
    right = load_from_file(env_file_b)
    tm = tag_by_prefix(left, {"DB_": "database"})
    left_db = filter_env_by_tag(left, tm, "database")
    right_db = filter_env_by_tag(right, tm, "database")
    result = diff_envs(left_db, right_db)
    assert "DB_HOST" in result.changed
    assert "DB_PORT" not in result.changed


def test_merge_then_diff_tags(env_file, env_file_b):
    left = load_from_file(env_file)
    right = load_from_file(env_file_b)
    tm_left = tag_by_prefix(left, {"AWS_": "cloud"})
    tm_right = tag_by_prefix(right, {"REDIS_": "cloud"})
    merged_tm = merge_tag_maps(tm_left, tm_right)
    assert "AWS_KEY" in merged_tm.keys_for("cloud")
    assert "REDIS_URL" in merged_tm.keys_for("cloud")
