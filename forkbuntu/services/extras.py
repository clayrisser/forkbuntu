from cfoundation import Service
from distutils.dir_util import copy_tree
from os import path
import os
import shutil
from glob import glob

class Extras(Service):
    def create(self):
        log = self.app.log
        c = self.app.conf
        s = self.app.services
        self.__load_indices()
        self.__generate_apt_ftparchive()
        if not path.isdir(path.join(c.paths.mount, 'dists/stable/extras/binary-amd64')):
            os.makedirs(path.join(c.paths.mount, 'dists/stable/extras/binary-amd64'))
        s.util.subproc(
            'apt-ftparchive packages ' + path.join(c.paths.mount, 'pool/extras') + ' > ' +
            path.join(c.paths.mount, 'dists/stable/extras/binary-amd64/Packages')
        )

    def __load_indices(self):
        s = self.app.services
        c = self.app.conf
        repo = 'http://archive.ubuntu.com/ubuntu/indices'
        if path.isdir(c.paths.indices):
            shutil.rmtree(c.paths.indices)
        os.makedirs(c.paths.indices)
        suffixes = [
            'extra.main',
            'main',
            'main.debian-installer',
            'restricted',
            'restricted.debian-installer'
        ]
        for suffix in suffixes:
            filename = 'override.' + c.codename + '.' + suffix
            s.util.subproc(
                'curl -L -o ' + path.join(c.paths.indices, filename) + ' ' + repo + ('/' + filename).replace('//', '')
            )

    def __generate_apt_ftparchive(self):
        s = self.app.services
        c = self.app.conf
        if path.isdir(c.paths.apt_ftparchive):
            shutil.rmtree(c.paths.apt_ftparchive)
        copy_tree(path.join(c.paths.src, 'apt-ftparchive'), c.paths.apt_ftparchive)
        for glob_path in glob(path.join(c.paths.apt_ftparchive, '*.conf')):
            s.util.stamp_template(
                glob_path,
                codename=c.codename,
                description=c.description,
                distrib_id=c.distrib_id,
                name=c.name,
                paths=c.paths,
                version=c.version
            )
