from cfoundation import Service
from distutils.dir_util import copy_tree
from os import path
from time import sleep
import os
import shutil

class Initrd(Service):
    def unpack(self):
        c = self.app.conf
        s = self.app.services
        if path.isdir(c.paths.initrd):
            shutil.rmtree(c.paths.initrd)
        os.makedirs(c.paths.initrd)
        os.chdir(c.paths.initrd)
        s.util.subproc(
            'gunzip -dc ' + path.join(c.paths.install, 'initrd.gz') +  ' | cpio -imvd --no-absolute-filenames',
            sudo=True
        )
        os.chdir(c.paths.cwd)

    def merge(self):
        c = self.app.conf
        if path.isdir(path.join(c.paths.cwd, 'initrd')):
            copy_tree(path.join(c.paths.cwd, 'initrd'), c.paths.initrd)

    def pack(self):
        c = self.app.conf
        s = self.app.services
        os.remove(path.join(c.paths.install, 'initrd.gz'))
        os.chdir(c.paths.initrd)
        s.util.subproc(
            'find . | cpio -o -H newc | gzip -9 > ' \
            + path.join(c.paths.install, 'initrd.gz'),
            sudo=True
        )
        os.chdir(c.paths.cwd)
