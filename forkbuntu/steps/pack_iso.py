from __future__ import annotations

from munch import Munch

from ..step import Step


class PackIso(Step):
    messages = Munch(past="packed iso", present="packing iso")
    requires = ["sign_iso"]

    def run(self, *args: object) -> None:
        s = self.app.services
        s.iso.pack()
