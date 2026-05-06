"""Tests for envdiff.grouper."""

import pytest

from envdiff.grouper import (
    EnvGroup,
    group_by_prefix,
    group_by_rules,
    merge_groups,
)


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "AWS_ACCESS_KEY": "AKIA…",
        "AWS_SECRET": "secret",
        "DEBUG": "true",
        "PORT": "8080",
    }


# --- EnvGroup ---

def test_env_group_len():
    g = EnvGroup(name="DB", keys=["DB_HOST", "DB_PORT"])
    assert len(g) == 2


def test_env_group_contains():
    g = EnvGroup(name="DB", keys=["DB_HOST"])
    assert "DB_HOST" in g
    assert "AWS_KEY" not in g


def test_env_group_as_dict():
    g = EnvGroup(name="DB", keys=["DB_PORT", "DB_HOST"])
    d = g.as_dict()
    assert d["name"] == "DB"
    assert d["count"] == 2
    assert d["keys"] == ["DB_HOST", "DB_PORT"]  # sorted


# --- group_by_prefix ---

def test_group_by_prefix_creates_db_group(sample_env):
    groups = group_by_prefix(sample_env)
    assert "DB" in groups
    assert len(groups["DB"]) == 3


def test_group_by_prefix_creates_aws_group(sample_env):
    groups = group_by_prefix(sample_env)
    assert "AWS" in groups
    assert len(groups["AWS"]) == 2


def test_group_by_prefix_ungrouped_catches_no_sep(sample_env):
    groups = group_by_prefix(sample_env)
    other = groups.get("OTHER")
    assert other is not None
    assert "DEBUG" in other
    assert "PORT" in other


def test_group_by_prefix_min_group_size(sample_env):
    # AWS has 2 keys; with min=3 it should fall into OTHER
    groups = group_by_prefix(sample_env, min_group_size=3)
    assert "AWS" not in groups
    assert "AWS_ACCESS_KEY" in groups["OTHER"]


def test_group_by_prefix_custom_sep():
    env = {"DB.HOST": "h", "DB.PORT": "p", "PLAIN": "v"}
    groups = group_by_prefix(env, sep=".")
    assert "DB" in groups
    assert len(groups["DB"]) == 2


def test_group_by_prefix_all_keys_accounted_for(sample_env):
    groups = group_by_prefix(sample_env)
    all_keys = {k for g in groups.values() for k in g.keys}
    assert all_keys == set(sample_env.keys())


# --- group_by_rules ---

def test_group_by_rules_assigns_correctly(sample_env):
    rules = {"Database": ["DB_"], "Cloud": ["AWS_"]}
    groups = group_by_rules(sample_env, rules)
    assert "DB_HOST" in groups["Database"]
    assert "AWS_SECRET" in groups["Cloud"]


def test_group_by_rules_leftover_in_other(sample_env):
    rules = {"Database": ["DB_"]}
    groups = group_by_rules(sample_env, rules)
    assert "OTHER" in groups
    assert "DEBUG" in groups["OTHER"]


def test_group_by_rules_all_keys_present(sample_env):
    rules = {"Database": ["DB_"], "Cloud": ["AWS_"]}
    groups = group_by_rules(sample_env, rules)
    all_keys = {k for g in groups.values() for k in g.keys}
    assert all_keys == set(sample_env.keys())


# --- merge_groups ---

def test_merge_groups_combines_keys():
    g1 = {"DB": EnvGroup("DB", ["DB_HOST"])}
    g2 = {"DB": EnvGroup("DB", ["DB_PORT"]), "AWS": EnvGroup("AWS", ["AWS_KEY"])}
    merged = merge_groups(g1, g2)
    assert len(merged["DB"]) == 2
    assert "AWS" in merged


def test_merge_groups_no_duplicates():
    g1 = {"DB": EnvGroup("DB", ["DB_HOST", "DB_PORT"])}
    g2 = {"DB": EnvGroup("DB", ["DB_HOST"])}
    merged = merge_groups(g1, g2)
    assert merged["DB"].keys.count("DB_HOST") == 1
