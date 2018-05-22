from cfoundation import Service
from os import path
from tempfile import gettempdir
import os
import shutil

class Unpack(Service):
    def mount_iso(self, iso_path, mount_path):
        iso_path = path.abspath(iso_path)
        tmp_mount_path = path.abspath(path.join(gettempdir(), 'forkbuntu', mount_path))
        mount_path = path.abspath(mount_path)
        os.system('umount ' + tmp_mount_path + ' 2>/dev/null')
        if path.isdir(tmp_mount_path):
            os.rmdir(tmp_mount_path)
        os.makedirs(tmp_mount_path)
        if path.isdir(mount_path):
            shutil.rmtree(mount_path)
        os.system('mount -o loop ' + iso_path + ' ' + tmp_mount_path)
        shutil.copytree(tmp_mount_path, mount_path, ignore=shutil.ignore_patterns('ubuntu'))
        os.system('umount ' + tmp_mount_path)
