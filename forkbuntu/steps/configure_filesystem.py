from __future__ import annotations

from munch import Munch

from ..step import Step


class ConfigureFilesystem(Step):
    messages = Munch(past="configured filesystem", present="configuring filesystem")
    requires = ["merge_filesystem"]

    def run(self, *args: object) -> None:
        s = self.app.services
        s.filesystem.configure()
