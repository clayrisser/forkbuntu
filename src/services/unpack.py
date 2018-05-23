from cfoundation import Service
from os import path
import os
import shutil

class Unpack(Service):
    def iso(self):
        c = self.app.conf
        tmp_mount_path = path.join(c.paths.tmp, 'iso')
        os.system('umount ' + tmp_mount_path + ' 2>/dev/null')
        if path.isdir(tmp_mount_path):
            shutil.rmtree(tmp_mount_path)
        os.makedirs(tmp_mount_path)
        if path.isdir(c.paths.mount):
            shutil.rmtree(c.paths.mount)
        os.system('mount -o loop ' + c.paths.iso + ' ' + tmp_mount_path)
        shutil.copytree(tmp_mount_path, c.paths.mount, ignore=shutil.ignore_patterns('ubuntu'))
        os.system('umount ' + tmp_mount_path)

    def filesystem(self):
        c = self.app.conf
        filesystem_parent_path = path.abspath(path.join(c.paths.filesystem, '..'))
        if path.isdir(path.join(filesystem_parent_path, 'squashfs-root')):
            shutil.rmtree(path.join(filesystem_parent_path, 'squashfs-root'))
        if path.isdir(c.paths.filesystem):
            shutil.rmtree(c.paths.filesystem)
        os.chdir(filesystem_parent_path)
        os.system('unsquashfs ' + path.join(c.paths.install, 'filesystem.squashfs'))
        os.chdir(c.paths.cwd)
        os.rename(path.join(filesystem_parent_path, 'squashfs-root'), c.paths.filesystem)
