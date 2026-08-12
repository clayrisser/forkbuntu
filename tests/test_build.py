from __future__ import annotations

import os
from typing import Any, Callable

import pytest
from munch import munchify

from forkbuntu.app import App

ubuntu_release = munchify(
    {
        "distrib_id": "Ubuntu",
        "distrib_release": "24.04",
        "distrib_codename": "noble",
        "distrib_description": "Ubuntu 24.04 LTS",
    }
)


def mock_pipeline(app: App, monkeypatch: pytest.MonkeyPatch, calls: list[str]) -> None:
    """Replace every side-effecting service call with a recorder so the
    step orchestration can run without root, xorriso, or a real iso.
    """
    s = app.services

    def record(name: str, result: Any = None) -> Callable[..., Any]:
        def _record(*args: Any, **kwargs: Any) -> Any:
            calls.append(name)
            return result

        return _record

    monkeypatch.setattr(s.setup, "init", record("setup.init"))

    def unpack_iso() -> None:
        calls.append("iso.unpack")
        os.makedirs(app.conf.paths.mount, exist_ok=True)

    monkeypatch.setattr(s.iso, "unpack", unpack_iso)
    monkeypatch.setattr(s.filesystem, "unpack", record("filesystem.unpack"))
    monkeypatch.setattr(
        s.configure, "load_release", record("load_release", ubuntu_release)
    )
    monkeypatch.setattr(s.filesystem, "merge", record("filesystem.merge"))
    monkeypatch.setattr(s.filesystem, "configure", record("filesystem.configure"))
    monkeypatch.setattr(s.filesystem, "pack", record("filesystem.pack"))
    monkeypatch.setattr(s.iso, "merge", record("iso.merge"))
    monkeypatch.setattr(s.iso, "sign", record("iso.sign"))

    def pack_iso() -> None:
        calls.append("iso.pack")
        with open(app.conf.paths.output, "w") as f:
            f.write("iso")

    monkeypatch.setattr(s.iso, "pack", pack_iso)


class TestBuild:
    def test_full_pipeline_order(
        self, make_app: Callable[..., App], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        app = make_app(output="out.iso")
        calls: list[str] = []
        mock_pipeline(app, monkeypatch, calls)
        assert app.build() == 0
        assert calls == [
            "setup.init",
            "iso.unpack",
            "filesystem.unpack",
            "load_release",
            "iso.merge",
            "filesystem.merge",
            "filesystem.configure",
            "filesystem.pack",
            "iso.sign",
            "iso.pack",
        ]
        assert os.path.exists(app.conf.paths.output)
        assert app.services.cache.is_finished() is True

    def test_second_build_uses_cache(
        self,
        make_app: Callable[..., App],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        app = make_app(output="out.iso")
        calls: list[str] = []
        mock_pipeline(app, monkeypatch, calls)
        app.build()
        first_calls = list(calls)
        app = make_app(output="out.iso")
        calls.clear()
        mock_pipeline(app, monkeypatch, calls)
        app.build()
        assert "iso.unpack" in first_calls
        # load_config re-derives in-memory conf on every run; every
        # side-effecting step is served from cache.
        assert calls == ["setup.init", "load_release"]

    def test_reset_flag_cleans_cache(
        self,
        make_app: Callable[..., App],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        app = make_app(output="out.iso")
        calls: list[str] = []
        mock_pipeline(app, monkeypatch, calls)
        app.build()
        app = make_app(output="out.iso", reset=True)
        calls.clear()
        mock_pipeline(app, monkeypatch, calls)
        app.build()
        assert "iso.unpack" in calls
