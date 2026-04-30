"""Validate environment variable keys and values against rules."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class ValidationError:
    key: str
    message: str

    def __str__(self) -> str:
        return f"{self.key}: {self.message}"


@dataclass
class ValidationResult:
    errors: List[ValidationError] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0

    def __len__(self) -> int:
        return len(self.errors)


Rule = Callable[[str, str], Optional[str]]


def rule_not_empty(key: str, value: str) -> Optional[str]:
    """Value must not be empty."""
    if value.strip() == "":
        return "value is empty"
    return None


def rule_no_spaces_in_key(key: str, value: str) -> Optional[str]:
    """Key must not contain spaces."""
    if " " in key:
        return "key contains spaces"
    return None


def rule_key_uppercase(key: str, value: str) -> Optional[str]:
    """Key should be uppercase."""
    if key != key.upper():
        return "key is not uppercase"
    return None


def rule_matches_pattern(pattern: str) -> Rule:
    """Return a rule that checks the value matches a regex pattern."""
    compiled = re.compile(pattern)

    def _rule(key: str, value: str) -> Optional[str]:
        if not compiled.fullmatch(value):
            return f"value does not match pattern '{pattern}'"
        return None

    return _rule


def validate_env(
    env: Dict[str, str],
    rules: Optional[List[Rule]] = None,
) -> ValidationResult:
    """Run all rules against every key/value pair in env."""
    if rules is None:
        rules = [rule_not_empty, rule_no_spaces_in_key]

    result = ValidationResult()
    for key, value in env.items():
        for rule in rules:
            msg = rule(key, value)
            if msg is not None:
                result.errors.append(ValidationError(key=key, message=msg))
    return result
