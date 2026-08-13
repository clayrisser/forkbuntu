from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

import pytest

from forkbuntu.app import App


def prepare_install(app: App, *squashfs_names: str) -> None:
    c = app.conf
    c.paths.install = os.path.join(c.paths.mount, "casper")
    os.makedirs(c.paths.install, exist_ok=True)
    for name in squashfs_names:
        with open(os.path.join(c.paths.install, name), "w") as f:
            f.write("squash")


class TestSquashfsPath:
    def test_default_filesystem_squashfs(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        prepare_install(app, "filesystem.squashfs")
        assert app.services.filesystem.squashfs_path().endswith("filesystem.squashfs")

    def test_single_candidate(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        prepare_install(app, "ubuntu-server-minimal.squashfs")
        assert app.services.filesystem.squashfs_path().endswith(
            "ubuntu-server-minimal.squashfs"
        )

    def test_explicit_config_wins(self, make_app: Callable[..., App]) -> None:
        app = make_app(config={"squashfs": "custom.squashfs"})
        prepare_install(app, "filesystem.squashfs", "custom.squashfs")
        assert app.services.filesystem.squashfs_path().endswith("custom.squashfs")

    def test_multiple_candidates_raise(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        prepare_install(app, "a.squashfs", "b.squashfs")
        with pytest.raises(Exception, match="set the `squashfs` config key"):
            app.services.filesystem.squashfs_path()

    def test_no_candidates_raise(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        prepare_install(app)
        with pytest.raises(Exception, match="no squashfs image found"):
            app.services.filesystem.squashfs_path()


class TestMerge:
    def test_stamps_lsb_release_and_applies_overlay(
        self, make_app: Callable[..., App]
    ) -> None:
        app = make_app()
        c = app.conf
        c.codename = "noble"
        c.name = "Testbuntu"
        c.version = "24.04"
        c.description = "Testbuntu 24.04"
        cwd = Path(c.paths.cwd)
        (cwd / "filesystem" / "etc").mkdir(parents=True)
        (cwd / "filesystem" / "etc" / "marker").write_text("marker")
        app.services.filesystem.merge()
        filesystem = Path(c.paths.filesystem)
        lsb_release = (filesystem / "etc" / "lsb-release").read_text()
        assert "DISTRIB_ID=Testbuntu" in lsb_release
        assert "DISTRIB_RELEASE=24.04" in lsb_release
        assert "DISTRIB_CODENAME=noble" in lsb_release
        assert 'DISTRIB_DESCRIPTION="Testbuntu 24.04"' in lsb_release
        assert (filesystem / "etc" / "marker").read_text() == "marker"


class TestPack:
    def _pack(self, app: App, compress: bool | int) -> list[str]:
        prepare_install(app, "filesystem.squashfs")
        app.conf.filesystem.compress = compress
        commands: list[list[str] | str] = []
        app.services.util.subproc = (  # type: ignore[method-assign]
            lambda command, sudo=False: commands.append(command) or "1024\n"
        )
        app.services.filesystem.pack()
        command = commands[0]
        assert isinstance(command, list)
        return command

    def test_no_compression_by_default(self, make_app: Callable[..., App]) -> None:
        command = self._pack(make_app(), False)
        assert command[0] == "mksquashfs"
        assert "-comp" not in command
        assert "-noappend" in command

    def test_compress_true_uses_xz(self, make_app: Callable[..., App]) -> None:
        command = self._pack(make_app(), True)
        assert command[command.index("-comp") + 1] == "xz"
        assert "-b" not in command

    def test_compress_number_sets_block_size(
        self, make_app: Callable[..., App]
    ) -> None:
        command = self._pack(make_app(), 1048576)
        assert command[command.index("-comp") + 1] == "xz"
        assert command[command.index("-b") + 1] == "1048576"

    def test_updates_filesystem_size_when_present(
        self, make_app: Callable[..., App]
    ) -> None:
        app = make_app()
        prepare_install(app, "filesystem.squashfs")
        size_path = os.path.join(app.conf.paths.install, "filesystem.size")
        with open(size_path, "w") as f:
            f.write("1")
        app.services.util.subproc = (  # type: ignore[method-assign]
            lambda command, sudo=False: "2048\n"
        )
        app.services.filesystem.pack()
        with open(size_path) as f:
            assert f.read() == "2048\n"
