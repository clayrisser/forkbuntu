from __future__ import annotations

from munch import Munch

from ..step import Step


class UnpackInitrd(Step):
    messages = Munch(past="unpacked initrd", present="unpacking initrd")
    requires = ["unpack_iso"]

    def run(self, *args: object) -> None:
        s = self.app.services
        s.initrd.unpack()
