from __future__ import annotations

from typing import Callable

import pytest

from forkbuntu.app import App

gpg_list_keys_output = """/root/.gnupg/pubring.kbx
------------------------
pub   rsa3072/0123456789ABCDEF 2024-01-01 [SC]
uid           [ultimate] Clay Risser <clay@example.com>
sub   rsa3072/FEDCBA9876543210 2024-01-01 [E]

pub   rsa1024/00000000FBB75451 2004-12-30 [SC]
uid           [ unknown] Ubuntu CD Image Automatic Signing Key <cdimage@ubuntu.com>

"""


class TestGetKeys:
    def test_parses_keys_and_filters_ubuntu(
        self, make_app: Callable[..., App], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        app = make_app()
        monkeypatch.setattr(
            app.services.util,
            "subproc",
            lambda command, sudo=False: gpg_list_keys_output,
        )
        keys = app.services.gpg.get_keys()
        assert len(keys) == 1
        key = keys[0]
        assert key.name == "Clay Risser"
        assert key.email == "clay@example.com"
        assert key.pub.key.long == "0123456789ABCDEF"
        assert key.pub.key.short == "89ABCDEF"
        assert key.pub.cipher == "rsa3072"
        assert key.sub.key.short == "76543210"

    def test_includes_ubuntu_keys_when_asked(
        self, make_app: Callable[..., App], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        app = make_app()
        monkeypatch.setattr(
            app.services.util,
            "subproc",
            lambda command, sudo=False: gpg_list_keys_output,
        )
        keys = app.services.gpg.get_keys(include_ubuntu_keys=True)
        assert len(keys) == 2

    def test_generates_key_when_none_found(
        self, make_app: Callable[..., App], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        app = make_app()
        generated: list[bool] = []
        outputs = iter(["no keys here", gpg_list_keys_output])
        monkeypatch.setattr(
            app.services.util,
            "subproc",
            lambda command, sudo=False: next(outputs),
        )
        monkeypatch.setattr(app.services.gpg, "gen_key", lambda: generated.append(True))
        keys = app.services.gpg.get_keys()
        assert generated == [True]
        assert len(keys) == 1


class TestGetKey:
    def test_single_key_selected(
        self, make_app: Callable[..., App], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        app = make_app()
        monkeypatch.setattr(
            app.services.util,
            "subproc",
            lambda command, sudo=False: gpg_list_keys_output,
        )
        app.gpg_keys = app.services.gpg.get_keys()
        key = app.services.gpg.get_key()
        assert key.email == "clay@example.com"

    def test_no_keys_raises(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        app.gpg_keys = []
        with pytest.raises(Exception, match="failed to find gpg key"):
            app.services.gpg.get_key()
