from __future__ import annotations

from forkbuntu.cli import parse_args


class TestParseArgs:
    def test_defaults_to_build(self) -> None:
        pargs = parse_args([])
        assert pargs.command == "build"
        assert pargs.src is None
        assert pargs.reset is False
        assert pargs.debug is False
        assert pargs.output == []

    def test_source_flag_variants(self) -> None:
        assert parse_args(["--source", "a"]).src == "a"
        assert parse_args(["--src", "b"]).src == "b"
        assert parse_args(["-s", "c"]).src == "c"

    def test_reset_flag(self) -> None:
        assert parse_args(["-r"]).reset is True
        assert parse_args(["--reset"]).reset is True

    def test_debug_flag(self) -> None:
        assert parse_args(["--debug"]).debug is True

    def test_output_positional(self) -> None:
        assert parse_args(["out.iso"]).output == ["out.iso"]

    def test_clean_command(self) -> None:
        pargs = parse_args(["clean", "-s", "example"])
        assert pargs.command == "clean"
        assert pargs.src == "example"

    def test_clean_only_recognized_as_first_argument(self) -> None:
        pargs = parse_args(["out.iso", "clean"])
        assert pargs.command == "build"
        assert pargs.output == ["out.iso", "clean"]
