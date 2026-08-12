from __future__ import annotations

from munch import Munch

from ..step import Step


class MergeInitrd(Step):
    messages = Munch(past="merged initrd", present="merging initrd")
    requires = ["unpack_initrd"]

    def run(self, *args: object) -> None:
        s = self.app.services
        s.initrd.merge()
