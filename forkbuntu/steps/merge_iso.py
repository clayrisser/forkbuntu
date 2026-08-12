from __future__ import annotations

from munch import Munch

from ..step import Step


class MergeIso(Step):
    messages = Munch(past="merged iso", present="merging iso")
    requires = ["load_config"]

    def run(self, *args: object) -> None:
        s = self.app.services
        s.iso.merge()
