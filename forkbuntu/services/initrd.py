from __future__ import annotations

import os
import shutil
from os import path

from ..service import Service


class Initrd(Service):
    def initrd_path(self) -> str:
        c = self.app.conf
        initrd_path = path.join(c.paths.install, "initrd.gz")
        if path.exists(initrd_path):
            return initrd_path
        if path.exists(path.join(c.paths.install, "initrd")):
            raise Exception(
                "initrd customization is only supported for gzip initrd.gz"
                + " images (debian-installer isos); modern casper initrd"
                + " images use concatenated archives"
            )
        raise Exception("no initrd.gz found in " + c.paths.install)

    def unpack(self) -> None:
        c = self.app.conf
        s = self.app.services
        initrd_path = self.initrd_path()
        if path.isdir(c.paths.initrd):
            shutil.rmtree(c.paths.initrd)
        os.makedirs(c.paths.initrd)
        os.chdir(c.paths.initrd)
        s.util.subproc(
            "gunzip -dc " + initrd_path + " | cpio -imd --no-absolute-filenames",
            sudo=True,
        )
        os.chdir(c.paths.cwd)

    def merge(self) -> None:
        c = self.app.conf
        if path.isdir(path.join(c.paths.cwd, "initrd")):
            shutil.copytree(
                path.join(c.paths.cwd, "initrd"), c.paths.initrd, dirs_exist_ok=True
            )

    def pack(self) -> None:
        c = self.app.conf
        s = self.app.services
        initrd_path = self.initrd_path()
        os.remove(initrd_path)
        os.chdir(c.paths.initrd)
        s.util.subproc(
            "find . | cpio -o -H newc | gzip -9 > " + initrd_path,
            sudo=True,
        )
        os.chdir(c.paths.cwd)
