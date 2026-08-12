from __future__ import annotations

import os
from typing import Callable

import pytest

from forkbuntu.app import App


def fake_which(missing: list[str]) -> Callable[[str], str | None]:
    def which(program: str) -> str | None:
        if program in missing:
            return None
        return "/usr/bin/" + program

    return which


class TestSetup:
    def test_exits_when_not_root(
        self, make_app: Callable[..., App], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        app = make_app()
        monkeypatch.setattr(os, "geteuid", lambda: 1000)
        with pytest.raises(SystemExit):
            app.services.setup.init()

    def test_passes_with_all_programs(
        self, make_app: Callable[..., App], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        app = make_app()
        monkeypatch.setattr(os, "geteuid", lambda: 0)
        monkeypatch.setattr("forkbuntu.services.setup.shutil.which", fake_which([]))
        app.services.setup.init()

    def test_exits_when_program_missing(
        self,
        make_app: Callable[..., App],
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        app = make_app()
        monkeypatch.setattr(os, "geteuid", lambda: 0)
        monkeypatch.setattr(
            "forkbuntu.services.setup.shutil.which", fake_which(["xorriso"])
        )
        with pytest.raises(SystemExit):
            app.services.setup.init()
        assert "xorriso" in capsys.readouterr().out

    def test_keyring_programs_only_checked_when_enabled(
        self, make_app: Callable[..., App], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(os, "geteuid", lambda: 0)
        monkeypatch.setattr(
            "forkbuntu.services.setup.shutil.which",
            fake_which(["dpkg-buildpackage", "fakeroot"]),
        )
        app = make_app()
        app.services.setup.init()
        app = make_app(config={"keyring": True})
        with pytest.raises(SystemExit):
            app.services.setup.init()

    def test_extras_programs_only_checked_with_extras_dir(
        self, make_app: Callable[..., App], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(os, "geteuid", lambda: 0)
        monkeypatch.setattr(
            "forkbuntu.services.setup.shutil.which", fake_which(["apt-ftparchive"])
        )
        app = make_app()
        app.services.setup.init()
        os.makedirs(os.path.join(app.conf.paths.cwd, "extras"))
        with pytest.raises(SystemExit):
            app.services.setup.init()

    def test_sudo_required_for_non_root_invoker(
        self, make_app: Callable[..., App], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(os, "geteuid", lambda: 0)
        monkeypatch.setattr(
            "forkbuntu.services.setup.shutil.which", fake_which(["sudo"])
        )
        app = make_app()
        monkeypatch.setattr(app.services.util, "get_real_user", lambda: "clay")
        with pytest.raises(SystemExit):
            app.services.setup.init()
        monkeypatch.setattr(app.services.util, "get_real_user", lambda: "root")
        app.services.setup.init()
