from __future__ import annotations

import os
import shutil
import sys
from os import path

from ..service import Service

core_programs = [
    "bash",
    "cat",
    "chmod",
    "chown",
    "chroot",
    "cpio",
    "curl",
    "cut",
    "du",
    "find",
    "gunzip",
    "gzip",
    "md5sum",
    "mksquashfs",
    "mount",
    "umount",
    "unsquashfs",
    "xorriso",
]
keyring_programs = [
    "apt-get",
    "dpkg-buildpackage",
    "fakeroot",
    "gpg",
]
extras_programs = [
    "apt-ftparchive",
]


class Setup(Service):
    def init(self) -> None:
        c = self.app.conf
        s = self.app.services
        spinner = self.app.spinner
        if os.geteuid() != 0:
            spinner.fail("please run as root")
            raise SystemExit(1)
        programs = list(core_programs)
        if s.util.get_real_user() != "root":
            programs.append("sudo")
        if c.keyring:
            programs += keyring_programs
        if path.isdir(path.join(c.paths.cwd, "extras")):
            programs += extras_programs
        missing_programs = [
            program for program in programs if not self._has_program(program)
        ]
        if len(missing_programs) > 0:
            spinner.fail("missing the following programs")
            sys.stdout.writelines([program + "\n" for program in missing_programs])
            raise SystemExit(1)

    def _has_program(self, program: str) -> bool:
        program_path = shutil.which(program)
        return bool(program_path)
