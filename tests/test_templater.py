"""Tests for envdiff.templater."""

import pytest

from envdiff.differ import DiffResult
from envdiff.templater import (
    TemplateOptions,
    diff_to_template,
    env_to_template,
    write_template,
)


@pytest.fixture()
def simple_env() -> dict[str, str]:
    return {"APP_NAME": "myapp", "DEBUG": "true", "PORT": "8080"}


@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        only_in_left={"LEFT_ONLY": "foo"},
        only_in_right={"RIGHT_ONLY": "bar"},
        changed={"SHARED": ("old", "new")},
        unchanged={"COMMON": "same"},
    )


def test_env_to_template_uses_placeholder(simple_env):
    out = env_to_template(simple_env)
    assert "APP_NAME=<FILL_ME>" in out
    assert "DEBUG=<FILL_ME>" in out


def test_env_to_template_custom_placeholder(simple_env):
    opts = TemplateOptions(placeholder="CHANGE_ME")
    out = env_to_template(simple_env, opts)
    assert "PORT=CHANGE_ME" in out


def test_env_to_template_include_values(simple_env):
    opts = TemplateOptions(include_values=True)
    out = env_to_template(simple_env, opts)
    assert "DEBUG=true" in out
    assert "PORT=8080" in out


def test_env_to_template_sorted_keys(simple_env):
    out = env_to_template(simple_env)
    keys = [line.split("=")[0] for line in out.strip().splitlines()]
    assert keys == sorted(keys)


def test_env_to_template_empty():
    assert env_to_template({}) == ""


def test_diff_to_template_contains_all_keys(diff_result):
    out = diff_to_template(diff_result)
    assert "LEFT_ONLY=" in out
    assert "RIGHT_ONLY=" in out
    assert "SHARED=" in out
    assert "COMMON=" in out


def test_diff_to_template_comments_for_only_left(diff_result):
    out = diff_to_template(diff_result)
    assert "# only in left" in out


def test_diff_to_template_comments_for_only_right(diff_result):
    out = diff_to_template(diff_result)
    assert "# only in right" in out


def test_diff_to_template_comments_for_changed(diff_result):
    out = diff_to_template(diff_result)
    assert "# changed:" in out
    assert "old" in out
    assert "new" in out


def test_diff_to_template_no_comments(diff_result):
    opts = TemplateOptions(include_comments=False)
    out = diff_to_template(diff_result, opts)
    assert "# only" not in out
    assert "# changed" not in out


def test_diff_to_template_unchanged_value_with_include_values(diff_result):
    opts = TemplateOptions(include_values=True)
    out = diff_to_template(diff_result, opts)
    assert "COMMON=same" in out


def test_write_template_creates_file(tmp_path):
    dest = tmp_path / "template.env"
    write_template(str(dest), "KEY=<FILL_ME>\n")
    assert dest.read_text() == "KEY=<FILL_ME>\n"
