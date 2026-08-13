from __future__ import annotations

from munch import Munch

from ..step import Step


class CreateExtras(Step):
    agnostic = True
    messages = Munch(past="created extras", present="creating extras")

    def init(self) -> None:
        c = self.app.conf
        # Rebuilding the archive keyring is only needed when the extras
        # repository must be trusted by the legacy debian-installer.
        self.requires = ["build_keyring"] if c.keyring else ["merge_iso"]
        self.checksum_paths = [
            c.paths.apt_ftparchive,
            c.paths.indices,
        ]

    def run(self, *args: object) -> None:
        s = self.app.services
        s.extras.create()
