from __future__ import annotations

from munch import Munch

from ..step import Step


class UnpackFilesystem(Step):
    messages = Munch(past="unpacked filesystem", present="unpacking filesystem")
    requires = ["unpack_iso"]

    def run(self, *args: object) -> None:
        s = self.app.services
        s.filesystem.unpack()
