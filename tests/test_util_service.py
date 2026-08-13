from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest

from forkbuntu.app import App


class TestGetRealUser:
    def test_sudo_user_wins(
        self, make_app: Callable[..., App], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        app = make_app()
        monkeypatch.setenv("SUDO_USER", "clay")
        assert app.services.util.get_real_user() == "clay"

    def test_falls_back_to_home_dir(
        self, make_app: Callable[..., App], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        app = make_app()
        monkeypatch.delenv("SUDO_USER", raising=False)
        monkeypatch.setattr(
            "forkbuntu.services.util.path.expanduser", lambda _: "/root"
        )
        assert app.services.util.get_real_user() == "root"


class TestSubproc:
    def _record_check_output(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> list[tuple[str | list[str], bool]]:
        calls: list[tuple[str | list[str], bool]] = []

        def fake_check_output(
            command: str | list[str], stderr: object = None, shell: bool = False
        ) -> bytes:
            calls.append((command, shell))
            return b"ok"

        monkeypatch.setattr("forkbuntu.services.util.check_output", fake_check_output)
        return calls

    def test_runs_directly_as_root(
        self, make_app: Callable[..., App], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        app = make_app()
        calls = self._record_check_output(monkeypatch)
        monkeypatch.setattr(app.services.util, "get_real_user", lambda: "root")
        app.services.util.subproc(["echo", "hi"])
        assert calls == [(["echo", "hi"], False)]

    def test_wraps_list_command_with_sudo_for_real_user(
        self, make_app: Callable[..., App], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        app = make_app()
        calls = self._record_check_output(monkeypatch)
        monkeypatch.setattr(app.services.util, "get_real_user", lambda: "clay")
        app.services.util.subproc(["echo", "hi"])
        assert calls == [
            (["sudo", "--preserve-env", "-u", "clay", "echo", "hi"], False)
        ]

    def test_wraps_string_command_with_sudo_for_real_user(
        self, make_app: Callable[..., App], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        app = make_app()
        calls = self._record_check_output(monkeypatch)
        monkeypatch.setattr(app.services.util, "get_real_user", lambda: "clay")
        app.services.util.subproc("echo hi")
        assert calls == [("sudo --preserve-env -u clay echo hi", True)]

    def test_sudo_true_never_wraps(
        self, make_app: Callable[..., App], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        app = make_app()
        calls = self._record_check_output(monkeypatch)
        monkeypatch.setattr(app.services.util, "get_real_user", lambda: "clay")
        app.services.util.subproc(["echo", "hi"], sudo=True)
        assert calls == [(["echo", "hi"], False)]

    def test_failure_exits_without_debug(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        with pytest.raises(SystemExit):
            app.services.util.subproc(["false"], sudo=True)

    def test_failure_raises_with_debug(self, make_app: Callable[..., App]) -> None:
        app = make_app(debug=True)
        with pytest.raises(Exception, match="returned non-zero exit status"):
            app.services.util.subproc(["false"], sudo=True)


class TestStampTemplate:
    def test_renders_in_place(
        self, make_app: Callable[..., App], tmp_path: Path
    ) -> None:
        app = make_app()
        template = tmp_path / "template.txt"
        template.write_text("hello {{ name }}")
        app.services.util.stamp_template(str(template), name="world")
        assert template.read_text() == "hello world\n"
