from __future__ import annotations

from os import path

from munch import Munch

from ..step import Step


class BuildKeyring(Step):
    agnostic = True
    messages = Munch(past="built keyring", present="building keyring")
    requires = [
        "merge_filesystem",
        "merge_iso",
    ]

    def init(self) -> None:
        c = self.app.conf
        self.checksum_paths = [
            c.paths.keyring,
            path.join(path.expanduser("~"), ".gnupg/pubring.kbx"),
        ]

    def run(self, *args: object) -> None:
        s = self.app.services
        s.gpg.build_keyring()
