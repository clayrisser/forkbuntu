from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

import yaml

from forkbuntu.app import App

grub_cfg = """set timeout=30
menuentry "Try or Install Ubuntu Server" {
	set gfxpayload=keep
	linux	/casper/vmlinuz  ---
	initrd	/casper/initrd
}
menuentry "Boot from next volume" {
	exit 1
}
"""


def prepare_conf(app: App, install: str = "casper") -> None:
    c = app.conf
    c.codename = "noble"
    c.origin = "Ubuntu"
    c.name = "Testbuntu"
    c.version = "24.04"
    c.description = "Testbuntu 24.04"
    c.hostname = "testbuntu"
    c.preseed = False
    c.paths.install = os.path.join(c.paths.mount, install)
    os.makedirs(c.paths.install, exist_ok=True)


class TestDetectInstallPath:
    def test_prefers_casper(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        os.makedirs(os.path.join(app.conf.paths.mount, "casper"))
        os.makedirs(os.path.join(app.conf.paths.mount, "install"))
        app.services.iso.detect_install_path()
        assert app.conf.paths.install.endswith("casper")

    def test_falls_back_to_install(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        os.makedirs(os.path.join(app.conf.paths.mount, "install"))
        app.services.iso.detect_install_path()
        assert app.conf.paths.install.endswith("install")


class TestMerge:
    def test_stamps_disk_info_and_diskdefines(
        self, make_app: Callable[..., App]
    ) -> None:
        app = make_app()
        prepare_conf(app)
        app.services.iso.merge()
        mount = Path(app.conf.paths.mount)
        assert (mount / ".disk" / "info").read_text().strip() == "Testbuntu 24.04"
        assert "Testbuntu 24.04" in (mount / "README.diskdefines").read_text()

    def test_copies_user_scripts_and_iso_overlay(
        self, make_app: Callable[..., App], tmp_path: Path
    ) -> None:
        app = make_app()
        prepare_conf(app)
        cwd = Path(app.conf.paths.cwd)
        (cwd / "scripts").mkdir()
        (cwd / "scripts" / "postinstall.sh").write_text("#!/bin/sh\n")
        (cwd / "iso" / ".disk").mkdir(parents=True)
        (cwd / "iso" / "marker.txt").write_text("marker")
        app.services.iso.merge()
        mount = Path(app.conf.paths.mount)
        assert (mount / "scripts" / "postinstall.sh").exists()
        assert (mount / "marker.txt").read_text() == "marker"
        assert (mount / "pool" / "extras").is_dir()

    def test_writes_preseed_for_debian_installer(
        self, make_app: Callable[..., App]
    ) -> None:
        app = make_app(config={"packages": ["cowsay", "vim"]})
        prepare_conf(app, install="install")
        app.conf.preseed = "testbuntu.seed"
        os.makedirs(os.path.join(app.conf.paths.mount, "isolinux"))
        app.services.iso.merge()
        mount = Path(app.conf.paths.mount)
        preseed = (mount / "preseed" / "testbuntu.seed").read_text()
        assert "cowsay" in preseed
        assert "vim" in preseed
        assert "d-i netcfg/get_hostname string testbuntu" in preseed
        txt_cfg = (mount / "isolinux" / "txt.cfg").read_text()
        assert "Install Testbuntu 24.04" in txt_cfg
        assert "file=/cdrom/preseed/testbuntu.seed" in txt_cfg
        assert "initrd=/install/initrd.gz" in txt_cfg

    def test_appends_user_preseed(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        prepare_conf(app, install="install")
        app.conf.preseed = "testbuntu.seed"
        cwd = Path(app.conf.paths.cwd)
        (cwd / "iso" / "preseed").mkdir(parents=True)
        (cwd / "iso" / "preseed" / "testbuntu.seed").write_text(
            "d-i custom/option boolean true\n"
        )
        app.services.iso.merge()
        preseed = (
            Path(app.conf.paths.mount) / "preseed" / "testbuntu.seed"
        ).read_text()
        assert "d-i custom/option boolean true" in preseed

    def test_skips_isolinux_when_absent(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        prepare_conf(app, install="install")
        app.conf.preseed = "testbuntu.seed"
        app.services.iso.merge()
        assert not (Path(app.conf.paths.mount) / "isolinux").exists()


class TestAutoinstall:
    def test_writes_seed_and_patches_grub(self, make_app: Callable[..., App]) -> None:
        app = make_app(
            config={
                "autoinstall": {"packages": ["cowsay"], "identity": {"hostname": "box"}}
            }
        )
        prepare_conf(app)
        mount = Path(app.conf.paths.mount)
        (mount / "boot" / "grub").mkdir(parents=True)
        (mount / "boot" / "grub" / "grub.cfg").write_text(grub_cfg)
        app.services.iso.merge()
        user_data = (mount / "autoinstall" / "user-data").read_text()
        assert user_data.startswith("#cloud-config\n")
        data = yaml.safe_load(user_data)
        assert data["autoinstall"]["version"] == 1
        assert data["autoinstall"]["packages"] == ["cowsay"]
        assert (mount / "autoinstall" / "meta-data").read_text() == ""
        patched = (mount / "boot" / "grub" / "grub.cfg").read_text()
        assert "autoinstall ds=nocloud\\;s=/cdrom/autoinstall/ ---" in patched
        assert "linux\t/casper/vmlinuz" in patched

    def test_respects_explicit_version(self, make_app: Callable[..., App]) -> None:
        app = make_app(config={"autoinstall": {"version": 2}})
        prepare_conf(app)
        app.services.iso.merge()
        user_data = (
            Path(app.conf.paths.mount) / "autoinstall" / "user-data"
        ).read_text()
        assert yaml.safe_load(user_data)["autoinstall"]["version"] == 2

    def test_skipped_when_not_configured(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        prepare_conf(app)
        app.services.iso.merge()
        assert not (Path(app.conf.paths.mount) / "autoinstall").exists()

    def test_patch_line_without_separator(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        line = app.services.iso._patch_grub_line("\tlinux /casper/vmlinuz quiet\n")
        assert line == (
            "\tlinux /casper/vmlinuz quiet"
            " autoinstall ds=nocloud\\;s=/cdrom/autoinstall/\n"
        )

    def test_patch_line_idempotent(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        line = "\tlinux /casper/vmlinuz autoinstall ds=nocloud\\;s=/cdrom/autoinstall/ ---\n"
        assert app.services.iso._patch_grub_line(line) == line

    def test_patch_ignores_unrelated_lines(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        line = "\tinitrd /casper/initrd\n"
        assert app.services.iso._patch_grub_line(line) == line


class TestBootArgs:
    def test_load_boot_args_filters_volume_id(
        self, make_app: Callable[..., App]
    ) -> None:
        app = make_app()
        os.makedirs(os.path.dirname(app.conf.paths.xorriso_args), exist_ok=True)
        with open(app.conf.paths.xorriso_args, "w") as f:
            f.write(
                "-V 'Ubuntu-Server 24.04.2 LTS amd64'\n"
                "--modification-date='2025021216490400'\n"
                "--grub2-mbr --interval:local_fs:0s-15s:zero_mbrpt:'/isos/base.iso'\n"
                "-partition_offset 16\n"
                "-c '/boot.catalog'\n"
                "-b '/boot/grub/i386-pc/eltorito.img'\n"
                "-no-emul-boot -boot-load-size 4 -boot-info-table --grub2-boot-info\n"
            )
        args = app.services.iso._load_boot_args()
        assert "-V" not in args
        assert "Ubuntu-Server 24.04.2 LTS amd64" not in args
        assert not any(arg.startswith("--modification-date=") for arg in args)
        assert "--grub2-mbr" in args
        assert "/boot/grub/i386-pc/eltorito.img" in args

    def test_load_boot_args_empty_when_missing(
        self, make_app: Callable[..., App]
    ) -> None:
        app = make_app()
        assert app.services.iso._load_boot_args() == []


class TestPack:
    def test_pack_uses_captured_boot_args(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        prepare_conf(app)
        os.makedirs(os.path.dirname(app.conf.paths.xorriso_args), exist_ok=True)
        with open(app.conf.paths.xorriso_args, "w") as f:
            f.write("-b '/boot/grub/i386-pc/eltorito.img'\n-no-emul-boot\n")
        commands: list[list[str] | str] = []
        app.services.util.subproc = (  # type: ignore[method-assign]
            lambda command, sudo=False: commands.append(command) or ""
        )
        app.services.iso.pack()
        command = commands[0]
        assert isinstance(command, list)
        assert command[:3] == ["xorriso", "-as", "mkisofs"]
        assert "-b" in command
        assert "/boot/grub/i386-pc/eltorito.img" in command
        assert app.conf.paths.output in command
        assert command[-1] == app.conf.paths.mount
        ubuntu_symlink = os.path.join(app.conf.paths.mount, "ubuntu")
        assert os.path.islink(ubuntu_symlink)
        assert os.readlink(ubuntu_symlink) == "."

    def test_pack_falls_back_to_isolinux(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        prepare_conf(app, install="install")
        os.makedirs(os.path.join(app.conf.paths.mount, "isolinux"))
        with open(
            os.path.join(app.conf.paths.mount, "isolinux/isolinux.bin"), "w"
        ) as f:
            f.write("")
        commands: list[list[str] | str] = []
        app.services.util.subproc = (  # type: ignore[method-assign]
            lambda command, sudo=False: commands.append(command) or ""
        )
        app.services.iso.pack()
        command = commands[0]
        assert isinstance(command, list)
        assert "isolinux/isolinux.bin" in command
        assert "-boot-info-table" in command

    def test_pack_warns_without_boot_info(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        prepare_conf(app)
        commands: list[list[str] | str] = []
        app.services.util.subproc = (  # type: ignore[method-assign]
            lambda command, sudo=False: commands.append(command) or ""
        )
        warnings: list[str] = []
        app.spinner.warn = lambda text="": warnings.append(text)  # type: ignore[method-assign]
        app.services.iso.pack()
        assert any("may not be bootable" in warning for warning in warnings)


class TestSign:
    def test_sign_generates_md5sums(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        prepare_conf(app)
        commands: list[list[str] | str] = []
        app.services.util.subproc = (  # type: ignore[method-assign]
            lambda command, sudo=False: commands.append(command) or ""
        )
        app.services.iso.sign()
        command = commands[0]
        assert isinstance(command, str)
        assert "md5sum > md5sum.txt" in command
        assert app.conf.paths.mount in command
