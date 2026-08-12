from __future__ import annotations

import os
from typing import Callable

import pytest

from forkbuntu.app import App


def prepare_install(app: App, *files: str) -> None:
    c = app.conf
    c.paths.install = os.path.join(c.paths.mount, "install")
    os.makedirs(c.paths.install, exist_ok=True)
    for name in files:
        with open(os.path.join(c.paths.install, name), "w") as f:
            f.write("")


class TestInitrdPath:
    def test_finds_initrd_gz(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        prepare_install(app, "initrd.gz")
        assert app.services.initrd.initrd_path().endswith("initrd.gz")

    def test_casper_initrd_not_supported(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        prepare_install(app, "initrd")
        with pytest.raises(Exception, match="only supported for gzip"):
            app.services.initrd.initrd_path()

    def test_missing_initrd_raises(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        prepare_install(app)
        with pytest.raises(Exception, match="no initrd.gz found"):
            app.services.initrd.initrd_path()
