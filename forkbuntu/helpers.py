from __future__ import annotations

import re
from typing import Any, cast

from munch import Munch, munchify

_boundary_regex = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_separator_regex = re.compile(r"[^a-zA-Z0-9]+")


def to_munch(data: dict[str, Any]) -> Munch:
    return cast(Munch, munchify(data))


def snake_case(value: str) -> str:
    value = _boundary_regex.sub("_", value)
    value = _separator_regex.sub("_", value)
    return value.strip("_").lower()


def deep_merge(*sources: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for source in sources:
        for key, value in source.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
    return result
