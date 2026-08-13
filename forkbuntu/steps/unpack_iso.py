from __future__ import annotations

from os import path

from munch import Munch

from ..step import Step


class UnpackIso(Step):
    messages = Munch(past="unpacked iso", present="unpacking iso")
    requires = ["initialize"]
    root = True

    def init(self) -> None:
        c = self.app.conf
        self.has_paths = [c.paths.output]
        self.checksum_paths = [
            c.paths.iso,
            c.paths.src,
            path.join(c.paths.cwd, "config.yml"),
            path.join(c.paths.cwd, "extras"),
            path.join(c.paths.cwd, "filesystem"),
            path.join(c.paths.cwd, "initrd"),
            path.join(c.paths.cwd, "iso"),
            path.join(c.paths.cwd, "scripts"),
        ]

    def run(self, *args: object) -> None:
        s = self.app.services
        s.iso.unpack()

    def cached(self, cached: bool) -> bool:
        # Even when the unpack is skipped, later steps need to know where
        # the installer payload lives on the iso.
        s = self.app.services
        s.iso.detect_install_path()
        return super().cached(cached)
