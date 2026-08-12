from __future__ import annotations

from munch import Munch

from ..step import Step


class PackFilesystem(Step):
    messages = Munch(past="packed filesystem", present="packing filesystem")
    requires = ["configure_filesystem"]

    def run(self, *args: object) -> None:
        s = self.app.services
        s.filesystem.pack()
