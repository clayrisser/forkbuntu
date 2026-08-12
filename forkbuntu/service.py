from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import App


class Service:
    def __init__(self, app: App) -> None:
        self.app = app
        self.log = app.log
