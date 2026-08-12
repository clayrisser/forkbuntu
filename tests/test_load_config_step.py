from __future__ import annotations

import os
from typing import Any, Callable

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


def run_load_config(app: App, install: str = "casper") -> None:
    app.conf.paths.install = os.path.join(app.conf.paths.mount, install)
    app.services.configure.load_release = lambda: ubuntu_release  # type: ignore[method-assign]
    app.steps.load_config.run()


class TestLoadConfig:
    def test_derives_identity_from_release(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        run_load_config(app)
        c = app.conf
        assert c.codename == "noble"
        assert c.origin == "Ubuntu"
        assert c.name == "Ubuntu"
        assert c.version == "24.04"
        assert c.description == "Ubuntu 24.04"
        assert c.hostname == "ubuntu"

    def test_config_values_win_over_release(self, make_app: Callable[..., App]) -> None:
        app = make_app(config={"name": "My Distro", "version": "1.0"})
        run_load_config(app)
        c = app.conf
        assert c.name == "My Distro"
        assert c.version == "1.0"
        assert c.description == "My Distro 1.0"
        assert c.hostname == "my-distro"

    def test_preseed_defaults_off_for_casper(
        self, make_app: Callable[..., App]
    ) -> None:
        app = make_app(config={"name": "My Distro"})
        run_load_config(app, install="casper")
        assert app.conf.preseed is False

    def test_preseed_defaults_on_for_debian_installer(
        self, make_app: Callable[..., App]
    ) -> None:
        app = make_app(config={"name": "My Distro"})
        run_load_config(app, install="install")
        assert app.conf.preseed == "my_distro.seed"

    def test_preseed_true_uses_name(self, make_app: Callable[..., App]) -> None:
        app = make_app(config={"name": "My Distro", "preseed": True})
        run_load_config(app, install="casper")
        assert app.conf.preseed == "my_distro.seed"

    def test_preseed_string_gets_seed_suffix(
        self, make_app: Callable[..., App]
    ) -> None:
        app = make_app(config={"preseed": "custom"})
        run_load_config(app)
        assert app.conf.preseed == "custom.seed"

    def test_preseed_string_keeps_seed_suffix(
        self, make_app: Callable[..., App]
    ) -> None:
        app = make_app(config={"preseed": "custom.seed"})
        run_load_config(app)
        assert app.conf.preseed == "custom.seed"

    def test_preseed_false_stays_off(self, make_app: Callable[..., App]) -> None:
        app = make_app(config={"preseed": False})
        run_load_config(app, install="install")
        assert app.conf.preseed is False
