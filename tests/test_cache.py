from __future__ import annotations

from pathlib import Path
from typing import Callable

from forkbuntu.app import App


class TestChecksum:
    def test_file_checksum_stable(
        self, make_app: Callable[..., App], tmp_path: Path
    ) -> None:
        app = make_app()
        target = tmp_path / "file.txt"
        target.write_text("content")
        first = app.services.cache.checksum(str(target))
        second = app.services.cache.checksum(str(target))
        assert first == second

    def test_file_checksum_changes_with_content(
        self, make_app: Callable[..., App], tmp_path: Path
    ) -> None:
        app = make_app()
        target = tmp_path / "file.txt"
        target.write_text("content")
        before = app.services.cache.checksum(str(target))
        target.write_text("changed")
        assert app.services.cache.checksum(str(target)) != before

    def test_dir_checksum_changes_with_new_file(
        self, make_app: Callable[..., App], tmp_path: Path
    ) -> None:
        app = make_app()
        target = tmp_path / "dir"
        target.mkdir()
        (target / "a.txt").write_text("a")
        before = app.services.cache.checksum(str(target))
        (target / "b.txt").write_text("b")
        assert app.services.cache.checksum(str(target)) != before

    def test_missing_path_hashes_path_string(
        self, make_app: Callable[..., App], tmp_path: Path
    ) -> None:
        app = make_app()
        missing = str(tmp_path / "missing")
        assert app.services.cache.checksum(missing) == app.services.cache.checksum(
            missing
        )


class TestCacheState:
    def test_register_and_get_checksums(
        self, make_app: Callable[..., App], tmp_path: Path
    ) -> None:
        app = make_app()
        tracked = tmp_path / "tracked.txt"
        tracked.write_text("content")
        app.steps.unpack_iso.checksum_paths = [str(tracked)]
        app.services.cache.register("unpack_iso")
        checksums = app.services.cache.get_checksums("unpack_iso")
        assert checksums == [app.services.cache.checksum(str(tracked))]

    def test_get_checksums_empty_for_unknown_key(
        self, make_app: Callable[..., App]
    ) -> None:
        app = make_app()
        assert app.services.cache.get_checksums("unknown") == []

    def test_finished_roundtrip(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        assert app.services.cache.is_finished() is False
        app.services.cache.finished()
        assert app.services.cache.is_finished() is True
        app.services.cache.started()
        assert app.services.cache.is_finished() is False
