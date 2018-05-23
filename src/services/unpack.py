from cfoundation import Service
from os import path
import os
import shutil

class Unpack(Service):
    def mount_iso(self):
        c = self.app.conf
        tmp_mount_path = path.join(c.paths.tmp, 'forkbuntu', 'iso')
        os.system('umount ' + tmp_mount_path + ' 2>/dev/null')
        if path.isdir(tmp_mount_path):
            shutil.rmtree(tmp_mount_path)
        os.makedirs(tmp_mount_path)
        if path.isdir(c.paths.mount):
            shutil.rmtree(c.paths.mount)
        os.system('mount -o loop ' + c.paths.iso + ' ' + tmp_mount_path)
        shutil.copytree(tmp_mount_path, c.paths.mount, ignore=shutil.ignore_patterns('ubuntu'))
        os.system('umount ' + tmp_mount_path)
