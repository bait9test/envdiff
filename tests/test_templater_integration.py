"""Integration tests for templater: roundtrip from file through diff to template."""

import pytest

from envdiff.differ import diff_envs
from envdiff.loader import load_from_file
from envdiff.templater import TemplateOptions, diff_to_template, env_to_template


@pytest.fixture()
def left_file(tmp_path):
    f = tmp_path / "left.env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc\n")
    return str(f)


@pytest.fixture()
def right_file(tmp_path):
    f = tmp_path / "right.env"
    f.write_text("DB_HOST=prodhost\nDB_PORT=5432\nNEW_FLAG=1\n")
    return str(f)


def test_single_file_template_has_all_keys(left_file):
    env = load_from_file(left_file)
    out = env_to_template(env)
    for key in env:
        assert f"{key}=" in out


def test_single_file_template_hides_values(left_file):
    env = load_from_file(left_file)
    out = env_to_template(env)
    assert "localhost" not in out
    assert "abc" not in out


def test_diff_template_marks_changed_key(left_file, right_file):
    left = load_from_file(left_file)
    right = load_from_file(right_file)
    result = diff_envs(left, right)
    out = diff_to_template(result)
    assert "# changed:" in out
    assert "DB_HOST=" in out


def test_diff_template_marks_only_in_left(left_file, right_file):
    left = load_from_file(left_file)
    right = load_from_file(right_file)
    result = diff_envs(left, right)
    out = diff_to_template(result)
    assert "# only in left" in out
    assert "SECRET=" in out


def test_diff_template_marks_only_in_right(left_file, right_file):
    left = load_from_file(left_file)
    right = load_from_file(right_file)
    result = diff_envs(left, right)
    out = diff_to_template(result)
    assert "# only in right" in out
    assert "NEW_FLAG=" in out


def test_diff_template_unchanged_key_no_comment(left_file, right_file):
    left = load_from_file(left_file)
    right = load_from_file(right_file)
    result = diff_envs(left, right)
    lines = diff_to_template(result).splitlines()
    port_idx = next(i for i, l in enumerate(lines) if l.startswith("DB_PORT="))
    if port_idx > 0:
        assert not lines[port_idx - 1].startswith("# only")
        assert not lines[port_idx - 1].startswith("# changed")


def test_diff_template_with_include_values_for_unchanged(left_file, right_file):
    left = load_from_file(left_file)
    right = load_from_file(right_file)
    result = diff_envs(left, right)
    opts = TemplateOptions(include_values=True)
    out = diff_to_template(result, opts)
    assert "DB_PORT=5432" in out
