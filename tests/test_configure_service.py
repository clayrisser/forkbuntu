from __future__ import annotations

import os
from typing import Callable

from forkbuntu.app import App


class TestLoadRelease:
    def _write_lsb_release(self, app: App, body: str) -> None:
        os.makedirs(os.path.join(app.conf.paths.filesystem, "etc"), exist_ok=True)
        with open(os.path.join(app.conf.paths.filesystem, "etc/lsb-release"), "w") as f:
            f.write(body)

    def test_parses_plain_values(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        self._write_lsb_release(
            app,
            "DISTRIB_ID=Ubuntu\n" "DISTRIB_RELEASE=24.04\n" "DISTRIB_CODENAME=noble\n",
        )
        release = app.services.configure.load_release()
        assert release.distrib_id == "Ubuntu"
        assert release.distrib_release == "24.04"
        assert release.distrib_codename == "noble"

    def test_strips_quotes(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        self._write_lsb_release(
            app,
            'DISTRIB_DESCRIPTION="Ubuntu 24.04 LTS"\n' "DISTRIB_CODENAME='noble'\n",
        )
        release = app.services.configure.load_release()
        assert release.distrib_description == "Ubuntu 24.04 LTS"
        assert release.distrib_codename == "noble"
