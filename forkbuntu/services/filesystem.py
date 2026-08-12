from __future__ import annotations

import os
import shutil
from glob import glob
from os import path
from subprocess import DEVNULL, call

from ..service import Service


class Filesystem(Service):
    def squashfs_path(self) -> str:
        """Locate the squashfs image to remaster inside the install dir.

        Modern live-server isos ship multiple layered squashfs images, so
        the image can be pinned with the ``squashfs`` config key.
        """
        c = self.app.conf
        if "squashfs" in c and c.squashfs:
            return path.join(c.paths.install, c.squashfs)
        default_path = path.join(c.paths.install, "filesystem.squashfs")
        if path.exists(default_path):
            return default_path
        candidates = glob(path.join(c.paths.install, "*.squashfs"))
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            raise Exception(
                "multiple squashfs images found; set the `squashfs` config key"
                + " to one of: "
                + ", ".join(sorted(path.basename(x) for x in candidates))
            )
        raise Exception("no squashfs image found in " + c.paths.install)

    def unpack(self) -> None:
        c = self.app.conf
        s = self.app.services
        if path.isdir(c.paths.filesystem):
            shutil.rmtree(c.paths.filesystem)
        os.makedirs(path.dirname(c.paths.filesystem), exist_ok=True)
        s.util.subproc(
            ["unsquashfs", "-d", c.paths.filesystem, self.squashfs_path()],
            sudo=True,
        )

    def merge(self) -> None:
        c = self.app.conf
        s = self.app.services
        if path.isdir(path.join(c.paths.src, "filesystem")):
            shutil.copytree(
                path.join(c.paths.src, "filesystem"),
                c.paths.filesystem,
                dirs_exist_ok=True,
            )
        s.util.stamp_template(
            path.join(c.paths.filesystem, "etc/lsb-release"),
            codename=c.codename,
            description=c.description,
            name=c.name,
            version=c.version,
        )
        if path.isdir(path.join(c.paths.cwd, "filesystem")):
            shutil.copytree(
                path.join(c.paths.cwd, "filesystem"),
                c.paths.filesystem,
                dirs_exist_ok=True,
            )

    def configure(self) -> None:
        c = self.app.conf
        log = self.app.log
        s = self.app.services
        resolv_path = path.join(c.paths.filesystem, "etc/resolv.conf")
        has_resolv = path.lexists(resolv_path)
        if has_resolv:
            os.rename(resolv_path, resolv_path + ".forkbuntu")
        shutil.copyfile(path.abspath("/etc/resolv.conf"), resolv_path)
        shutil.copytree(
            path.join(c.paths.mount, "scripts"),
            path.join(c.paths.filesystem, "root/scripts"),
            dirs_exist_ok=True,
        )
        # Bind mounts require CAP_SYS_ADMIN which unprivileged containers
        # lack; degrade gracefully since simple configure scripts work
        # without them.
        mounts = [
            ["mount", "--bind", "/dev", path.join(c.paths.filesystem, "dev")],
            ["mount", "-t", "proc", "none", path.join(c.paths.filesystem, "proc")],
            ["mount", "-t", "sysfs", "none", path.join(c.paths.filesystem, "sys")],
            [
                "mount",
                "-t",
                "devpts",
                "none",
                path.join(c.paths.filesystem, "dev/pts"),
            ],
        ]
        mounted: list[str] = []
        for mount_command in mounts:
            if call(mount_command, stdout=DEVNULL, stderr=DEVNULL) == 0:
                mounted.append(mount_command[-1])
            else:
                log.warning("failed to mount " + mount_command[-1])
        try:
            env = dict(os.environ)
            env["HOME"] = "/root"
            env["LC_ALL"] = "C"
            command = [
                "chroot",
                c.paths.filesystem,
                "/bin/sh",
                "/root/scripts/filesystem.sh",
            ]
            log.debug("command: " + " ".join(command))
            if call(command, env=env) != 0:
                raise Exception("filesystem configure script failed")
        finally:
            for mount_path in reversed(mounted):
                if call(["umount", mount_path], stdout=DEVNULL, stderr=DEVNULL) != 0:
                    call(["umount", "-lf", mount_path], stdout=DEVNULL, stderr=DEVNULL)
            shutil.rmtree(path.join(c.paths.filesystem, "root/scripts"))
            os.remove(resolv_path)
            if has_resolv:
                os.rename(resolv_path + ".forkbuntu", resolv_path)

    def pack(self) -> None:
        c = self.app.conf
        log = self.app.log
        s = self.app.services
        compress: list[str] = []
        if c.filesystem.compress:
            compress = ["-comp", "xz"]
            if isinstance(c.filesystem.compress, int) and not isinstance(
                c.filesystem.compress, bool
            ):
                compress += ["-b", str(c.filesystem.compress)]
        squashfs_path = self.squashfs_path()
        os.remove(squashfs_path)
        s.util.subproc(
            ["mksquashfs", c.paths.filesystem, squashfs_path, "-noappend"] + compress,
            sudo=True,
        )
        size_path = path.join(c.paths.install, "filesystem.size")
        if path.exists(size_path):
            size = s.util.subproc(
                "du -sx --block-size=1 " + c.paths.filesystem + " | cut -f1",
                sudo=True,
            )
            log.debug("size: " + size)
            with open(size_path, "w") as f:
                f.write(size)
