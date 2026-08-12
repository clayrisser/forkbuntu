from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
from os import path

import yaml
from munch import unmunchify

from ..service import Service

# Kernel command line that points subiquity at the cloud-init seed baked
# into the ISO. The semicolon must be escaped for GRUB.
autoinstall_cmdline = "autoinstall ds=nocloud\\;s=/cdrom/autoinstall/"


class Iso(Service):
    def unpack(self) -> None:
        c = self.app.conf
        log = self.app.log
        s = self.app.services
        if path.isdir(c.paths.mount):
            shutil.rmtree(c.paths.mount)
        os.makedirs(path.dirname(c.paths.mount), exist_ok=True)
        s.util.subproc(
            [
                "xorriso",
                "-osirrox",
                "on",
                "-indev",
                c.paths.iso,
                "-extract",
                "/",
                c.paths.mount,
            ],
            sudo=True,
        )
        # xorriso preserves the read-only permissions recorded on the ISO;
        # make the tree writable so it can be merged and repacked.
        s.util.subproc(["chmod", "-R", "u+w", c.paths.mount], sudo=True)
        self._capture_boot_args()
        self.detect_install_path()
        log.debug("install path: " + c.paths.install)

    def detect_install_path(self) -> None:
        c = self.app.conf
        for candidate in ["casper", "install"]:
            if path.isdir(path.join(c.paths.mount, candidate)):
                c.paths.install = path.join(c.paths.mount, candidate)
                return
        c.paths.install = path.join(c.paths.mount, "install")

    def merge(self) -> None:
        c = self.app.conf
        s = self.app.services
        if path.isdir(path.join(c.paths.src, "iso")):
            shutil.copytree(
                path.join(c.paths.src, "iso"), c.paths.mount, dirs_exist_ok=True
            )
        if path.exists(path.join(c.paths.mount, ".disk", "info")):
            s.util.stamp_template(
                path.join(c.paths.mount, ".disk", "info"), description=c.description
            )
        if path.exists(path.join(c.paths.mount, "README.diskdefines")):
            s.util.stamp_template(
                path.join(c.paths.mount, "README.diskdefines"),
                description=c.description,
            )
        if path.isdir(path.join(c.paths.cwd, "scripts")):
            shutil.copytree(
                path.join(c.paths.cwd, "scripts"),
                path.join(c.paths.mount, "scripts"),
                dirs_exist_ok=True,
            )
        if path.isdir(path.join(c.paths.cwd, "extras")):
            shutil.copytree(
                path.join(c.paths.cwd, "extras"),
                path.join(c.paths.mount, "pool/extras"),
                dirs_exist_ok=True,
            )
        if not path.isdir(path.join(c.paths.mount, "pool/extras")):
            os.makedirs(path.join(c.paths.mount, "pool/extras"))
        if path.isdir(path.join(c.paths.cwd, "iso")):
            shutil.copytree(
                path.join(c.paths.cwd, "iso"), c.paths.mount, dirs_exist_ok=True
            )
        self._write_isolinux()
        self._write_preseed()
        self._write_autoinstall()

    def sign(self) -> None:
        c = self.app.conf
        s = self.app.services
        s.util.subproc(
            "cd "
            + shlex.quote(c.paths.mount)
            + " && find . -path ./isolinux -prune -o -path ./md5sum.txt -prune"
            + " -o -type f -print0 | xargs -0 md5sum > md5sum.txt",
            sudo=True,
        )

    def pack(self) -> None:
        c = self.app.conf
        log = self.app.log
        s = self.app.services
        spinner = self.app.spinner
        ubuntu_symlink_path = path.join(c.paths.mount, "ubuntu")
        if not path.lexists(ubuntu_symlink_path):
            os.symlink(".", ubuntu_symlink_path)
        boot_args = self._load_boot_args()
        if len(boot_args) <= 0:
            if path.exists(path.join(c.paths.mount, "isolinux/isolinux.bin")):
                boot_args = [
                    "-b",
                    "isolinux/isolinux.bin",
                    "-c",
                    "isolinux/boot.cat",
                    "-no-emul-boot",
                    "-boot-load-size",
                    "4",
                    "-boot-info-table",
                ]
            else:
                spinner.warn("no boot information found; iso may not be bootable")
                spinner.start()
        s.util.subproc(
            [
                "xorriso",
                "-as",
                "mkisofs",
                "-r",
                "-V",
                c.name + " Install CD",
                "-J",
                "-joliet-long",
                "-l",
                "-o",
                c.paths.output,
            ]
            + boot_args
            + [c.paths.mount],
            sudo=True,
        )
        log.debug("packed iso: " + c.paths.output)

    def _capture_boot_args(self) -> None:
        c = self.app.conf
        log = self.app.log
        result = subprocess.run(
            [
                "xorriso",
                "-indev",
                c.paths.iso,
                "-report_el_torito",
                "as_mkisofs",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            log.warning("failed to capture boot arguments: " + result.stderr)
            return
        os.makedirs(path.dirname(c.paths.xorriso_args), exist_ok=True)
        with open(c.paths.xorriso_args, "w") as f:
            f.write(result.stdout)
        log.debug("boot arguments: " + result.stdout)

    def _load_boot_args(self) -> list[str]:
        c = self.app.conf
        if not path.exists(c.paths.xorriso_args):
            return []
        with open(c.paths.xorriso_args) as f:
            args = shlex.split(f.read(), comments=True)
        # Volume id and modification date describe the source iso; the
        # repacked iso provides its own.
        boot_args: list[str] = []
        skip_next = False
        for arg in args:
            if skip_next:
                skip_next = False
                continue
            if arg == "-V":
                skip_next = True
                continue
            if arg.startswith("--modification-date="):
                continue
            boot_args.append(arg)
        return boot_args

    def _write_isolinux(self) -> None:
        c = self.app.conf
        s = self.app.services
        if not c.preseed:
            return
        if not path.isdir(path.join(c.paths.mount, "isolinux")):
            return
        shutil.copy(
            path.join(c.paths.src, "isolinux/txt.cfg"),
            path.join(c.paths.mount, "isolinux/txt.cfg"),
        )
        s.util.stamp_template(
            path.join(c.paths.mount, "isolinux/txt.cfg"),
            description=c.description,
            preseed=c.preseed,
            install=path.basename(c.paths.install),
        )
        if path.exists(path.join(c.paths.cwd, "iso/isolinux/txt.cfg")):
            self._append_file(
                path.join(c.paths.cwd, "iso/isolinux/txt.cfg"),
                path.join(c.paths.mount, "isolinux/txt.cfg"),
            )

    def _write_preseed(self) -> None:
        c = self.app.conf
        s = self.app.services
        if not c.preseed:
            return
        preseed_dir = path.join(c.paths.mount, "preseed")
        os.makedirs(preseed_dir, exist_ok=True)
        shutil.copy(
            path.join(c.paths.src, "preseed.seed"),
            path.join(preseed_dir, c.preseed),
        )
        s.util.stamp_template(
            path.join(preseed_dir, c.preseed),
            apt=c.apt,
            hostname=c.hostname,
            packages=c.packages,
        )
        if path.exists(path.join(c.paths.cwd, "iso/preseed", c.preseed)):
            self._append_file(
                path.join(c.paths.cwd, "iso/preseed", c.preseed),
                path.join(preseed_dir, c.preseed),
            )

    def _write_autoinstall(self) -> None:
        c = self.app.conf
        if not c.autoinstall:
            return
        autoinstall = unmunchify(c.autoinstall)
        if "version" not in autoinstall:
            autoinstall["version"] = 1
        autoinstall_dir = path.join(c.paths.mount, "autoinstall")
        os.makedirs(autoinstall_dir, exist_ok=True)
        with open(path.join(autoinstall_dir, "user-data"), "w") as f:
            f.write(
                "#cloud-config\n"
                + yaml.safe_dump({"autoinstall": autoinstall}, default_flow_style=False)
            )
        with open(path.join(autoinstall_dir, "meta-data"), "w") as f:
            f.write("")
        self._patch_grub()

    def _patch_grub(self) -> None:
        c = self.app.conf
        log = self.app.log
        for name in ["grub.cfg", "loopback.cfg"]:
            grub_path = path.join(c.paths.mount, "boot/grub", name)
            if not path.exists(grub_path):
                continue
            with open(grub_path) as f:
                lines = f.readlines()
            patched = [self._patch_grub_line(line) for line in lines]
            with open(grub_path, "w") as f:
                f.writelines(patched)
            log.debug("patched " + grub_path + " for autoinstall")

    def _patch_grub_line(self, line: str) -> str:
        if not re.match(r"^\s*linux(16)?\s+\S*vmlinuz\S*", line):
            return line
        if "autoinstall" in line:
            return line
        stripped = line.rstrip("\n")
        if re.search(r"\s---(\s|$)", stripped):
            return (
                re.sub(r"\s---(\s|$)", " " + autoinstall_cmdline + r" ---\1", stripped)
                + "\n"
            )
        return stripped + " " + autoinstall_cmdline + "\n"

    def _append_file(self, source_path: str, target_path: str) -> None:
        with open(target_path) as f:
            lines = f.readlines()
        lines.append("\n")
        with open(source_path) as f:
            lines += f.readlines()
        with open(target_path, "w") as f:
            f.writelines(lines)
