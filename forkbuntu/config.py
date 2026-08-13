from __future__ import annotations

import os
from os import path
from tempfile import mkdtemp

import yaml
from munch import Munch

from .helpers import deep_merge, to_munch


class ConfigError(Exception):
    pass


def default_conf() -> Munch:
    return to_munch(
        {
            "apt": {
                "restricted": True,
                "universe": True,
                "multiarch": True,
            },
            "autoinstall": {},
            "debug": False,
            "filesystem": {
                "compress": False,
            },
            "keyring": False,
            "packages": [],
            "paths": {
                "apt_ftparchive": ".tmp/apt-ftparchive",
                "cwd": os.getcwd(),
                "cwt": ".tmp",
                "filesystem": ".tmp/filesystem",
                "indices": ".tmp/indices",
                "initrd": ".tmp/initrd",
                "iso": "ubuntu-24.04-live-server-amd64.iso",
                "keyring": ".tmp/keyring",
                "mount": ".tmp/iso",
                "output": "forkbuntu.iso",
                "src": path.dirname(path.realpath(__file__)),
                "xorriso_args": ".tmp/xorriso-args.txt",
            },
        }
    )


def load_conf(
    src: str | None = None,
    output: str | None = None,
    debug: bool = False,
) -> Munch:
    conf = default_conf()
    cwd_path = path.abspath(src) if src else os.getcwd()
    config_path = path.join(cwd_path, "config.yml")
    if not path.exists(config_path):
        raise ConfigError("config not found: " + config_path)
    with open(config_path) as f:
        try:
            data = yaml.safe_load(f) or {}
        except yaml.YAMLError as err:
            raise ConfigError("invalid config: " + str(err)) from err
    if not isinstance(data, dict):
        raise ConfigError("invalid config: expected a mapping")
    conf = to_munch(deep_merge(conf, data))
    conf.paths.cwd = cwd_path
    conf.debug = bool(conf.debug or debug)
    if "version" in conf:
        conf.version = str(conf.version)
    # Output resolves against the invocation directory, every other path
    # against the source directory.
    output_path = output if output else conf.paths.output
    conf = to_munch(
        deep_merge(
            conf,
            {
                "paths": {
                    key: path.abspath(path.join(conf.paths.cwd, value))
                    for key, value in conf.paths.items()
                }
            },
        )
    )
    conf.paths.output = path.abspath(output_path)
    # Where the installer payload (squashfs, initrd) lives on the ISO. The
    # real location is only known once the ISO has been unpacked; see
    # Iso.detect_install_path().
    conf.paths.install = path.join(conf.paths.mount, "install")
    conf.paths.tmp = mkdtemp(prefix="forkbuntu-")
    return conf
