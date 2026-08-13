from __future__ import annotations

import os
import shutil
from glob import glob
from os import path

from ..service import Service

indices_repo = "http://archive.ubuntu.com/ubuntu/indices"
indices_suffixes = [
    "extra.main",
    "main",
    "main.debian-installer",
    "restricted",
    "restricted.debian-installer",
]


class Extras(Service):
    def create(self) -> None:
        c = self.app.conf
        s = self.app.services
        self._load_indices()
        self._generate_apt_ftparchive()
        binary_path = path.join(c.paths.mount, "dists/stable/extras/binary-amd64")
        if not path.isdir(binary_path):
            os.makedirs(binary_path)
        s.util.subproc(
            "apt-ftparchive packages "
            + path.join(c.paths.mount, "pool/extras")
            + " > "
            + path.join(binary_path, "Packages")
        )

    def _load_indices(self) -> None:
        s = self.app.services
        c = self.app.conf
        if path.isdir(c.paths.indices):
            shutil.rmtree(c.paths.indices)
        os.makedirs(c.paths.indices)
        for suffix in indices_suffixes:
            filename = "override." + c.codename + "." + suffix
            s.util.download(
                indices_repo + "/" + filename, path.join(c.paths.indices, filename)
            )
        s.util.chown(c.paths.indices)

    def _generate_apt_ftparchive(self) -> None:
        s = self.app.services
        c = self.app.conf
        if path.isdir(c.paths.apt_ftparchive):
            shutil.rmtree(c.paths.apt_ftparchive)
        shutil.copytree(
            path.join(c.paths.src, "apt-ftparchive"), c.paths.apt_ftparchive
        )
        for glob_path in glob(path.join(c.paths.apt_ftparchive, "*.conf")):
            s.util.stamp_template(
                glob_path,
                codename=c.codename,
                description=c.description,
                name=c.name,
                origin=c.origin,
                paths=c.paths,
                version=c.version,
            )
        s.util.chown(c.paths.apt_ftparchive)
