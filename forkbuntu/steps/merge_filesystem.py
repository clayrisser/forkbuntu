from __future__ import annotations

from munch import Munch

from ..step import Step


class MergeFilesystem(Step):
    messages = Munch(past="merged filesystem", present="merging filesystem")
    requires = ["load_config"]

    def run(self, *args: object) -> None:
        s = self.app.services
        s.filesystem.merge()
