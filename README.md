# forkbuntu

> Easily create your own Ubuntu distribution and install CD

![](assets/forkbuntu.png)

Please ★ this repo if you found it useful ★ ★ ★

## Features

- Simple config file
- Rebrand the filesystem and iso metadata
- Overlay custom files onto the filesystem and iso
- Run configure scripts inside the unpacked filesystem (chroot)
- Autoinstall support for modern subiquity isos (Ubuntu 20.04+)
- Preseed support for legacy debian-installer isos (Ubuntu 18.04 and older)
- Add custom packages and postinstall scripts
- Incremental rebuilds via content checksums

## Installation

```sh
uv tool install forkbuntu
```

## Dependencies

- [Python 3.12+](https://www.python.org)
- [xorriso](https://www.gnu.org/software/xorriso)
- [Squashfs Tools](https://github.com/plougher/squashfs-tools)
- [GnuPG](https://www.gnupg.org) (only for the legacy `keyring` flow)

On Ubuntu:

```sh
sudo apt-get install xorriso squashfs-tools
```

## Usage

Create a directory with a `config.yml` and place the base Ubuntu iso next
to it (see [example](example)):

```yaml
name: Forkbuntu
version: '24.04'
paths:
  iso: ubuntu-24.04-live-server-amd64.iso
  output: forkbuntu.iso
autoinstall:
  packages:
    - cowsay
```

Then build the iso:

```sh
sudo forkbuntu -s example
```

Building must run as root on a Linux host because the filesystem is
configured inside a chroot and squashfs ownership must be preserved.
Everything except the chroot bind mounts also works inside an unprivileged
Ubuntu container (see `make test/e2e`).

### Customization

| path            | purpose                                                          |
| --------------- | ---------------------------------------------------------------- |
| `config.yml`    | build configuration                                               |
| `filesystem/`   | files copied over the unpacked squashfs filesystem                |
| `iso/`          | files copied over the iso tree                                    |
| `scripts/`      | scripts shipped on the iso; `filesystem.sh` runs in the chroot    |
| `extras/`       | extra `.deb` packages published on the iso as an apt component    |
| `initrd/`       | files merged into the initrd (legacy `initrd.gz` isos only)       |

### Configuration

| key                   | default                | purpose                                                     |
| --------------------- | ---------------------- | ------------------------------------------------------------ |
| `name`                | from the base iso      | distribution name                                            |
| `version`             | from the base iso      | distribution version                                         |
| `description`         | `<name> <version>`     | branding used in `.disk/info`, `lsb-release`, boot menus     |
| `hostname`            | derived from `name`    | preseeded hostname (legacy debian-installer only)            |
| `paths.iso`           | —                      | base Ubuntu iso                                              |
| `paths.output`        | `forkbuntu.iso`        | output iso path (relative to the invocation directory)       |
| `squashfs`            | auto-detected          | squashfs image to remaster on multi-layer isos               |
| `autoinstall`         | —                      | [subiquity autoinstall](https://canonical-subiquity.readthedocs-hosted.com/en/latest/reference/autoinstall-reference.html) config baked into the iso |
| `preseed`             | auto (d-i isos only)   | preseed name, `true`/`false` to force                        |
| `packages`            | `[]`                   | packages installed by the preseed (legacy debian-installer)  |
| `apt`                 | all enabled            | `restricted`/`universe`/`multiarch` preseed toggles          |
| `filesystem.compress` | `false`                | `true` for xz, or a number for the xz block size             |
| `keyring`             | `false`                | rebuild the ubuntu-keyring with your gpg key (legacy d-i)    |

For modern isos the `autoinstall` mapping is written to
`/autoinstall/user-data` on the iso (as cloud-init `#cloud-config`) and the
GRUB kernel command line is updated to
`autoinstall ds=nocloud\;s=/cdrom/autoinstall/` automatically.

## Development

```sh
make prepare   # one-time toolchain setup (asdf + uv sync)
make test      # unit tests with coverage
make lint      # black + basedpyright + shfmt
make format    # auto-format
make test/e2e  # full pipeline against a fixture iso in an ubuntu:24.04 container
```

## Support

Submit an [issue](https://gitlab.com/bitspur/misc/forkbuntu/-/issues/new)

## Contributing

Review the [guidelines for contributing](CONTRIBUTING.md)

## License

[MIT License](LICENSE)

[Clay Risser](https://clayrisser.com) © 2018

## Changelog

Review the [changelog](CHANGELOG.md)

## Credits

- [Clay Risser](https://clayrisser.com) - Author
- [Ubuntu Autoinstall Reference](https://canonical-subiquity.readthedocs-hosted.com/en/latest/reference/autoinstall-reference.html)
- [Debian Installer Preseed](https://people.debian.org/~plessy/DebianInstallerDebconfTemplates.html)
- [Ubuntu Derivative Distro How to](https://wiki.ubuntu.com/DerivativeDistroHowto)
- [Ubuntu Install CD Customization](https://help.ubuntu.com/community/InstallCDCustomization)
- [Ubuntu Live CD Customization](https://help.ubuntu.com/community/LiveCDCustomization)
