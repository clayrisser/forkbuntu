#!/bin/sh
# End-to-end remaster of a tiny fixture iso. Runs as root inside an
# ubuntu:24.04 container (see `make test/e2e`) with the repository
# mounted at /opt/forkbuntu.
set -e

repo="${FORKBUNTU_REPO:-/opt/forkbuntu}"
work=$(mktemp -d)

fail() {
    echo "FAIL: $1" >&2
    exit 1
}

echo '::: installing system dependencies :::'
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -yq --no-install-recommends \
    busybox-static \
    ca-certificates \
    cpio \
    curl \
    squashfs-tools \
    xorriso

echo '::: installing uv :::'
curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null
PATH="$HOME/.local/bin:$PATH"
export PATH
# Keep the container venv out of the host checkout mounted at $repo.
UV_PROJECT_ENVIRONMENT="$work/venv"
export UV_PROJECT_ENVIRONMENT
UV_LINK_MODE=copy
export UV_LINK_MODE

echo '::: syncing project :::'
uv sync --frozen --project "$repo"

echo '::: running unit tests :::'
(cd "$repo" && uv run --project "$repo" pytest -p no:cacheprovider -q)

echo '::: building fixture iso :::'
rootfs="$work/rootfs"
mkdir -p "$rootfs/bin" "$rootfs/etc" "$rootfs/root"
cp "$(command -v busybox)" "$rootfs/bin/busybox"
ln -s busybox "$rootfs/bin/sh"
cat >"$rootfs/etc/lsb-release" <<EOF
DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=24.04
DISTRIB_CODENAME=noble
DISTRIB_DESCRIPTION="Ubuntu 24.04 LTS"
EOF
echo 'nameserver 127.0.0.53' >"$rootfs/etc/resolv.conf"
isotree="$work/isotree"
mkdir -p "$isotree/casper" "$isotree/boot/grub"
mksquashfs "$rootfs" "$isotree/casper/filesystem.squashfs" -quiet -no-progress
printf 'menuentry "Try or Install Ubuntu Server" {\n\tset gfxpayload=keep\n\tlinux\t/casper/vmlinuz  ---\n\tinitrd\t/casper/initrd\n}\n' \
    >"$isotree/boot/grub/grub.cfg"
xorriso -as mkisofs -r -V 'Fixture' -o "$work/fixture.iso" "$isotree" 2>/dev/null

echo '::: building forkbuntu iso :::'
src="$work/src"
mkdir -p "$src/filesystem/etc"
echo 'e2e marker' >"$src/filesystem/etc/forkbuntu-e2e"
cat >"$src/config.yml" <<EOF
name: Testbuntu
version: '24.04'
paths:
  iso: ../fixture.iso
  output: testbuntu.iso
autoinstall:
  packages:
    - cowsay
EOF
(cd "$src" && uv run --project "$repo" forkbuntu)

echo '::: verifying output iso :::'
out="$work/out"
[ -f "$src/testbuntu.iso" ] || fail 'output iso was not created'
xorriso -osirrox on -indev "$src/testbuntu.iso" -extract / "$out" 2>/dev/null
chmod -R u+w "$out"
grep -q 'Testbuntu 24.04' "$out/.disk/info" || fail '.disk/info was not stamped'
grep -q 'Testbuntu 24.04' "$out/README.diskdefines" ||
    fail 'README.diskdefines was not stamped'
grep -q 'autoinstall ds=nocloud' "$out/boot/grub/grub.cfg" ||
    fail 'grub.cfg was not patched for autoinstall'
grep -q 'cowsay' "$out/autoinstall/user-data" ||
    fail 'autoinstall user-data is missing packages'
grep -q '#cloud-config' "$out/autoinstall/user-data" ||
    fail 'autoinstall user-data is missing the cloud-config header'
[ -f "$out/autoinstall/meta-data" ] || fail 'autoinstall meta-data is missing'
[ -f "$out/md5sum.txt" ] || fail 'md5sum.txt is missing'
outfs="$work/outfs"
unsquashfs -q -no-progress -d "$outfs" "$out/casper/filesystem.squashfs"
grep -q 'DISTRIB_DESCRIPTION="Testbuntu 24.04"' "$outfs/etc/lsb-release" ||
    fail 'filesystem lsb-release was not stamped'
grep -q 'e2e marker' "$outfs/etc/forkbuntu-e2e" ||
    fail 'filesystem overlay was not applied'
[ -e "$outfs/root/scripts" ] && fail 'configure scripts were not cleaned up'
grep -q '127.0.0.53' "$outfs/etc/resolv.conf" ||
    fail 'resolv.conf was not restored'

echo '::: verifying cache reuse :::'
second=$(cd "$src" && uv run --project "$repo" forkbuntu 2>&1) || {
    echo "$second"
    fail 'second build failed'
}
echo "$second" | grep -q 'using cache' || fail 'second build did not use cache'

echo '::: e2e passed :::'
