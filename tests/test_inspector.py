"""Tests for envdiff.inspector."""

import pytest

from envdiff.inspector import KeyInspection, inspect_all, inspect_key


ENV_A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true", "URL": "http://a.com"}
ENV_B = {"HOST": "prod.example.com", "PORT": "5432", "EXTRA": "only-b"}


@pytest.fixture
def envs():
    return {"a": ENV_A, "b": ENV_B}


def test_inspect_key_present_in(envs):
    insp = inspect_key("HOST", envs)
    assert "a" in insp.present_in
    assert "b" in insp.present_in


def test_inspect_key_missing_from(envs):
    insp = inspect_key("EXTRA", envs)
    assert "a" in insp.missing_from
    assert "b" not in insp.missing_from


def test_inspect_key_consistent_when_equal(envs):
    insp = inspect_key("PORT", envs)
    assert insp.is_consistent is True


def test_inspect_key_not_consistent_when_different(envs):
    insp = inspect_key("HOST", envs)
    assert insp.is_consistent is False


def test_inspect_key_consistent_when_missing_in_one(envs):
    # EXTRA only exists in b; a returns None — values differ, so not consistent
    insp = inspect_key("EXTRA", envs)
    assert insp.is_consistent is False


def test_inferred_type_numeric(envs):
    insp = inspect_key("PORT", envs)
    assert insp.inferred_types["a"] == "numeric"
    assert insp.inferred_types["b"] == "numeric"


def test_inferred_type_boolean(envs):
    insp = inspect_key("DEBUG", envs)
    assert insp.inferred_types["a"] == "boolean"


def test_inferred_type_url(envs):
    insp = inspect_key("URL", envs)
    assert insp.inferred_types["a"] == "url"


def test_inferred_type_missing(envs):
    insp = inspect_key("URL", envs)
    assert insp.inferred_types["b"] == "missing"


def test_type_consistent_when_same_type(envs):
    insp = inspect_key("PORT", envs)
    assert insp.type_consistent is True


def test_type_inconsistent_when_types_differ():
    envs = {"x": {"FOO": "true"}, "y": {"FOO": "http://example.com"}}
    insp = inspect_key("FOO", envs)
    assert insp.type_consistent is False


def test_inspect_all_covers_all_keys(envs):
    inspections = inspect_all(envs)
    keys = {i.key for i in inspections}
    assert keys == {"HOST", "PORT", "DEBUG", "URL", "EXTRA"}


def test_inspect_all_sorted(envs):
    inspections = inspect_all(envs)
    keys = [i.key for i in inspections]
    assert keys == sorted(keys)


def test_as_dict_has_expected_fields(envs):
    insp = inspect_key("PORT", envs)
    d = insp.as_dict()
    assert "key" in d
    assert "sources" in d
    assert "is_consistent" in d
    assert "inferred_types" in d
    assert "type_consistent" in d
