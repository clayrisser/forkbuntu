from __future__ import annotations

import os
import re
import shlex
import shutil
from glob import glob
from os import path

import inquirer
from munch import Munch, munchify

from ..service import Service

ubuntu_keys = ["FBB75451", "437D05B5", "C0B21F32", "EFE21092"]


class GPG(Service):
    def setup(self) -> None:
        gpg_path = path.join(path.expanduser("~"), ".gnupg")
        private_keys_path = path.join(gpg_path, "private-keys-v1.d")
        if not path.exists(private_keys_path):
            os.makedirs(private_keys_path)
            self._chmod_gpg()

    def build_keyring(self) -> None:
        c = self.app.conf
        s = self.app.services
        if path.isdir(c.paths.keyring):
            shutil.rmtree(c.paths.keyring)
        os.makedirs(c.paths.keyring)
        s.util.chown(c.paths.keyring)
        os.chdir(c.paths.keyring)
        s.util.subproc("apt-get source ubuntu-keyring")
        s.util.chown(c.paths.keyring)
        keyring_dirs = [
            entry
            for entry in os.listdir(c.paths.keyring)
            if path.isdir(path.join(c.paths.keyring, entry))
        ]
        if len(keyring_dirs) <= 0:
            raise Exception("failed to source ubuntu-keyring")
        ubuntu_keyring_path = path.join(c.paths.keyring, keyring_dirs[0])
        keyrings_path = path.join(ubuntu_keyring_path, "keyrings")
        os.chdir(keyrings_path)
        s.util.subproc(
            "gpg --import < " + path.join(keyrings_path, "ubuntu-archive-keyring.gpg")
        )
        gpg_key = self.get_key()
        s.util.subproc(
            "gpg --export "
            + " ".join(ubuntu_keys)
            + " "
            + gpg_key.pub.key.short
            + " > "
            + path.join(keyrings_path, "ubuntu-archive-keyring.gpg")
        )
        os.chdir(ubuntu_keyring_path)
        stdout = s.util.subproc(
            "cat "
            + path.join(keyrings_path, "ubuntu-archive-keyring.gpg")
            + " | sha512sum"
        )
        sha512sum = stdout.split(" ")[0]
        lines = []
        with open(path.join(ubuntu_keyring_path, "SHA512SUMS.txt.asc")) as f:
            for line in f.readlines():
                line = re.sub(
                    r"(\w+)(?=\s+keyrings/ubuntu-archive-keyring.gpg)", sha512sum, line
                )
                lines.append(line)
        with open(path.join(ubuntu_keyring_path, "SHA512SUMS.txt.asc"), "w") as f:
            f.writelines(lines)
        self.app.spinner.stop()
        s.util.subproc(
            'dpkg-buildpackage -rfakeroot -m"'
            + gpg_key.name
            + " <"
            + gpg_key.email
            + '>" -k'
            + gpg_key.pub.key.short
        )
        self.app.spinner.start()
        keyring_debs = glob(path.join(c.paths.keyring, "ubuntu-keyring*.deb"))
        if len(keyring_debs) <= 0:
            raise Exception("failed to build ubuntu-keyring")
        keyring_deb_path = keyring_debs[0]
        pool_path = path.join(c.paths.mount, "pool/main/u/ubuntu-keyring")
        if path.isdir(pool_path):
            for deb_path in keyring_debs:
                shutil.copy(deb_path, pool_path)
        for keyring_path in [
            "usr/share/keyrings/ubuntu-archive-keyring.gpg",
            "etc/apt/trusted.gpg",
            "var/lib/apt/keyrings/ubuntu-archive-keyring.gpg",
        ]:
            target_path = path.join(c.paths.filesystem, keyring_path)
            os.makedirs(path.dirname(target_path), exist_ok=True)
            shutil.copyfile(
                path.join(keyrings_path, "ubuntu-archive-keyring.gpg"), target_path
            )
        os.chdir(c.paths.cwd)

    def gen_key(self) -> None:
        s = self.app.services
        spinner = self.app.spinner
        self._chmod_gpg()
        spinner.stop()
        s.util.subproc("gpg --gen-key")
        spinner.start()

    def get_keys(
        self, include_ubuntu_keys: bool = False, trying_again: bool = False
    ) -> list[Munch]:
        s = self.app.services
        keys = []
        stdout = s.util.subproc("gpg --keyid-format LONG --list-keys")
        matches = re.split(r"-{4}\n", stdout)
        stdout_keys = []
        if len(matches) > 1:
            stdout_keys = list(filter(None, matches[1].split("\n\n")))
        for stdout_key in stdout_keys:
            key = Munch()
            lines = stdout_key.split("\n")
            if len(lines) >= 2:
                match = next(
                    re.finditer(r"(pub\s+)(\w+)\/(\w+)\s+([\w-]+)", lines[0]), None
                )
                if match:
                    key_long = match.groups()[2].strip()
                    key.pub = munchify(
                        {
                            "cipher": match.groups()[1].strip(),
                            "key": {
                                "long": key_long,
                                "short": key_long[8:],
                            },
                            "date": match.groups()[3].strip(),
                        }
                    )
                match = next(
                    re.finditer(r"(uid\s+\[.+]\s+)(.+)(<[^<>]+>)", lines[1]), None
                )
                if match:
                    email = match.groups()[2].strip()
                    key.name = match.groups()[1].strip()
                    key.email = email[1 : len(email) - 1]
            if len(lines) >= 3:
                match = next(
                    re.finditer(r"(sub\s+)(\w+)\/(\w+)\s+([\w-]+)", lines[2]), None
                )
                if match:
                    key_long = match.groups()[2].strip()
                    key.sub = munchify(
                        {
                            "cipher": match.groups()[1].strip(),
                            "key": {
                                "long": key_long,
                                "short": key_long[8:],
                            },
                            "date": match.groups()[3].strip(),
                        }
                    )
            if not ("pub" in key and "name" in key and "email" in key):
                continue
            if not include_ubuntu_keys:
                if key.pub.key.short in ubuntu_keys:
                    continue
            keys.append(key)
        if len(keys) <= 0:
            if trying_again:
                self.app.spinner.fail("failed to load gpg keys")
                raise SystemExit(1)
            self.gen_key()
            return self.get_keys(trying_again=True)
        return keys

    def get_key(self) -> Munch:
        spinner = self.app.spinner
        gpg_keys = self.app.gpg_keys
        gpg_key = None
        if len(gpg_keys) == 1:
            gpg_key = gpg_keys[0]
        elif len(gpg_keys) > 1:
            spinner.stop()
            answer = munchify(
                inquirer.prompt(
                    [
                        inquirer.List(
                            "gpg_key",
                            message="choose a gpg key",
                            choices=[
                                key.pub.key.short
                                + ": "
                                + key.name
                                + " <"
                                + key.email
                                + ">"
                                for key in gpg_keys
                            ],
                        )
                    ]
                )
            ).gpg_key
            spinner.start()
            gpg_key = next(
                (
                    key
                    for key in gpg_keys
                    if key.pub.key.short == answer[: answer.index(":")]
                ),
                None,
            )
        if not gpg_key:
            raise Exception("failed to find gpg key")
        return gpg_key

    def _chmod_gpg(self) -> None:
        s = self.app.services
        gpg_path = path.join(path.expanduser("~"), ".gnupg")
        s.util.chown(gpg_path)
        s.util.subproc(["chmod", "700", gpg_path], sudo=True)
        s.util.subproc(
            "find " + shlex.quote(gpg_path) + r" -type f -exec chmod 600 {} \;",
            sudo=True,
        )
