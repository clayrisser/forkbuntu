from __future__ import annotations

from munch import Munch

from ..step import Step


class PackInitrd(Step):
    messages = Munch(past="packed initrd", present="packing initrd")
    requires = ["merge_initrd"]

    def run(self, *args: object) -> None:
        s = self.app.services
        s.initrd.pack()
