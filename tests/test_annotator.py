"""Tests for envdiff.annotator."""

import pytest

from envdiff.annotator import (
    Annotation,
    annotate,
    build_annotation_map,
    annotate_env,
    format_annotated_dotenv,
)


def test_annotation_str_no_tags():
    a = Annotation(key="DB_HOST", comment="Database hostname")
    assert str(a) == "# Database hostname"


def test_annotation_str_with_tags():
    a = Annotation(key="SECRET", comment="Keep secret", tags=["sensitive", "infra"])
    result = str(a)
    assert "# Keep secret" in result
    assert "# tags: infra, sensitive" in result


def test_annotate_factory():
    a = annotate("PORT", "Server port", ["network"])
    assert a.key == "PORT"
    assert a.comment == "Server port"
    assert a.tags == ["network"]


def test_annotate_no_tags_defaults_empty():
    a = annotate("PORT", "Server port")
    assert a.tags == []


def test_build_annotation_map_indexes_by_key():
    a1 = annotate("A", "first")
    a2 = annotate("B", "second")
    amap = build_annotation_map([a1, a2])
    assert "A" in amap
    assert "B" in amap
    assert amap["A"].comment == "first"


def test_build_annotation_map_empty():
    assert build_annotation_map([]) == {}


def test_annotate_env_filters_unannotated():
    env = {"A": "1", "B": "2", "C": "3"}
    amap = build_annotation_map([annotate("A", "has annotation")])
    result = annotate_env(env, amap)
    assert result == {"A": "1"}


def test_annotate_env_all_annotated():
    env = {"X": "foo", "Y": "bar"}
    amap = build_annotation_map([annotate("X", "ex"), annotate("Y", "why")])
    result = annotate_env(env, amap)
    assert result == env


def test_format_annotated_dotenv_includes_comment():
    env = {"HOST": "localhost"}
    amap = build_annotation_map([annotate("HOST", "The host")])
    output = format_annotated_dotenv(env, amap)
    assert "# The host" in output
    assert "HOST=localhost" in output


def test_format_annotated_dotenv_unannotated_included_by_default():
    env = {"HOST": "localhost", "PORT": "5432"}
    amap = build_annotation_map([annotate("HOST", "The host")])
    output = format_annotated_dotenv(env, amap)
    assert "PORT=5432" in output


def test_format_annotated_dotenv_only_annotated_excludes_others():
    env = {"HOST": "localhost", "PORT": "5432"}
    amap = build_annotation_map([annotate("HOST", "The host")])
    output = format_annotated_dotenv(env, amap, include_unannotated=False)
    assert "HOST=localhost" in output
    assert "PORT" not in output


def test_format_annotated_dotenv_tag_appears_in_output():
    env = {"TOKEN": "abc123"}
    amap = build_annotation_map([annotate("TOKEN", "Auth token", ["sensitive"])])
    output = format_annotated_dotenv(env, amap)
    assert "tags: sensitive" in output
