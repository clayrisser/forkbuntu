from __future__ import annotations

from forkbuntu.helpers import deep_merge, snake_case


class TestSnakeCase:
    def test_lowercases_single_word(self) -> None:
        assert snake_case("Forkbuntu") == "forkbuntu"

    def test_splits_spaces(self) -> None:
        assert snake_case("My Distro") == "my_distro"

    def test_splits_camel_case(self) -> None:
        assert snake_case("someCamelCase") == "some_camel_case"

    def test_collapses_separators(self) -> None:
        assert snake_case("a - b -- c") == "a_b_c"

    def test_keeps_numbers(self) -> None:
        assert snake_case("Ubuntu 24.04") == "ubuntu_24_04"


class TestDeepMerge:
    def test_merges_flat_keys(self) -> None:
        assert deep_merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}

    def test_later_sources_win(self) -> None:
        assert deep_merge({"a": 1}, {"a": 2}) == {"a": 2}

    def test_merges_nested_dicts(self) -> None:
        result = deep_merge({"a": {"b": 1, "c": 2}}, {"a": {"c": 3}})
        assert result == {"a": {"b": 1, "c": 3}}

    def test_replaces_lists(self) -> None:
        assert deep_merge({"a": [1, 2]}, {"a": [3]}) == {"a": [3]}

    def test_does_not_mutate_sources(self) -> None:
        first = {"a": {"b": 1}}
        deep_merge(first, {"a": {"b": 2}})
        assert first == {"a": {"b": 1}}
