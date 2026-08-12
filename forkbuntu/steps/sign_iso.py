from __future__ import annotations

from os import path

from munch import Munch

from ..step import Step


class SignIso(Step):
    messages = Munch(past="signed iso", present="signing iso")

    def init(self) -> None:
        c = self.app.conf
        requires = ["merge_iso", "pack_filesystem"]
        if path.isdir(path.join(c.paths.cwd, "extras")):
            requires.append("create_extras")
        if path.isdir(path.join(c.paths.cwd, "initrd")):
            requires.append("pack_initrd")
        self.requires = requires

    def run(self, *args: object) -> None:
        s = self.app.services
        s.iso.sign()
