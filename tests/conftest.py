from __future__ import annotations

from argparse import Namespace
from pathlib import Path
from typing import Any, Callable

import pytest
import yaml

from forkbuntu.app import App


def write_config(src_path: Path, config: dict[str, Any] | None = None) -> Path:
    config = config or {}
    src_path.mkdir(parents=True, exist_ok=True)
    with open(src_path / "config.yml", "w") as f:
        yaml.safe_dump(config, f)
    return src_path


@pytest.fixture
def make_app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Callable[..., App]:
    def _make_app(
        config: dict[str, Any] | None = None,
        output: str | None = None,
        reset: bool = False,
        debug: bool = False,
    ) -> App:
        src_path = write_config(tmp_path / "src", config)
        pargs = Namespace(
            src=str(src_path),
            reset=reset,
            debug=debug,
            output=[output] if output else [],
            command="build",
        )
        app = App(pargs)
        # Keep spinner animation threads out of pytest's captured streams.
        app.spinner.enabled = False
        # Tests never run as root, so never try to chown artifacts back to
        # the invoking user (which would shell out to sudo).
        monkeypatch.setattr(app.services.util, "chown", lambda *args, **kwargs: None)
        return app

    return _make_app
