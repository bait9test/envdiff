"""Tests for envdiff.tagger."""

import pytest
from envdiff.tagger import (
    TagMap,
    tag_by_prefix,
    tag_by_pattern,
    merge_tag_maps,
    filter_env_by_tag,
)

SAMPLE_ENV = {
    "AWS_ACCESS_KEY_ID": "AKIA123",
    "AWS_SECRET_ACCESS_KEY": "secret",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_DEBUG": "true",
    "APP_URL": "http://example.com",
    "PLAIN_KEY": "value",
}


def test_tag_map_add_and_retrieve():
    tm = TagMap()
    tm.add("aws", "AWS_ACCESS_KEY_ID")
    assert "aws" in tm.tags_for("AWS_ACCESS_KEY_ID")


def test_tag_map_tags_for_untagged_key():
    tm = TagMap()
    assert tm.tags_for("UNKNOWN") == []


def test_tag_map_keys_for_missing_tag():
    tm = TagMap()
    assert tm.keys_for("ghost") == set()


def test_tag_map_all_tags_sorted():
    tm = TagMap()
    tm.add("z_tag", "K1")
    tm.add("a_tag", "K2")
    assert tm.all_tags() == ["a_tag", "z_tag"]


def test_tag_map_as_dict():
    tm = TagMap()
    tm.add("aws", "AWS_KEY")
    tm.add("aws", "AWS_SECRET")
    d = tm.as_dict()
    assert set(d["aws"]) == {"AWS_KEY", "AWS_SECRET"}


def test_tag_by_prefix_basic():
    tm = tag_by_prefix(SAMPLE_ENV, {"AWS_": "aws", "DB_": "database"})
    assert "AWS_ACCESS_KEY_ID" in tm.keys_for("aws")
    assert "AWS_SECRET_ACCESS_KEY" in tm.keys_for("aws")
    assert "DB_HOST" in tm.keys_for("database")
    assert "DB_PORT" in tm.keys_for("database")


def test_tag_by_prefix_no_match():
    tm = tag_by_prefix(SAMPLE_ENV, {"NOMATCH_": "ghost"})
    assert tm.keys_for("ghost") == set()


def test_tag_by_pattern_wildcard():
    tm = tag_by_pattern(SAMPLE_ENV, {"*URL*": "network", "*SECRET*": "sensitive"})
    assert "APP_URL" in tm.keys_for("network")
    assert "AWS_SECRET_ACCESS_KEY" in tm.keys_for("sensitive")


def test_tag_by_pattern_no_match():
    tm = tag_by_pattern(SAMPLE_ENV, {"*NOTHING*": "empty"})
    assert tm.keys_for("empty") == set()


def test_merge_tag_maps_combines_keys():
    tm1 = tag_by_prefix(SAMPLE_ENV, {"AWS_": "cloud"})
    tm2 = tag_by_prefix(SAMPLE_ENV, {"DB_": "cloud"})
    merged = merge_tag_maps(tm1, tm2)
    cloud_keys = merged.keys_for("cloud")
    assert "AWS_ACCESS_KEY_ID" in cloud_keys
    assert "DB_HOST" in cloud_keys


def test_merge_tag_maps_empty():
    merged = merge_tag_maps()
    assert merged.all_tags() == []


def test_filter_env_by_tag():
    tm = tag_by_prefix(SAMPLE_ENV, {"DB_": "database"})
    filtered = filter_env_by_tag(SAMPLE_ENV, tm, "database")
    assert set(filtered.keys()) == {"DB_HOST", "DB_PORT"}
    assert filtered["DB_HOST"] == "localhost"


def test_filter_env_by_tag_unknown_tag_returns_empty():
    tm = TagMap()
    filtered = filter_env_by_tag(SAMPLE_ENV, tm, "nonexistent")
    assert filtered == {}
