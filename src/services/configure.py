from cfoundation import Service
from distutils.dir_util import copy_tree
from jinja2 import Template
from os import path
import os

class Configure(Service):
    def merge_files(self, working_path, mount_path, packages):
        src_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), '..'))
        working_path = path.abspath(working_path)
        mount_path = path.abspath(mount_path)
        copy_tree(path.join(src_path, 'iso'), mount_path)
        self.__preseed(mount_path, packages)
        if path.isdir(path.join(working_path, 'scripts')):
            copy_tree(path.join(working_path, 'scripts'), path.join(mount_path, 'scripts'))
        if path.isdir(path.join(working_path, 'iso')):
            copy_tree(path.join(working_path, 'iso'), mount_path)

    def __preseed(self, mount_path, packages):
        mount_path = path.abspath(mount_path)
        preseed = ''
        with open(path.join(mount_path, 'preseed', 'forkbuntu.seed'), 'r') as f:
            preseed = f.read()
        template = Template(preseed)
        preseed = template.render(packages=packages) + '\n'
        with open(path.join(mount_path, 'preseed', 'forkbuntu.seed'), 'w') as f:
            f.write(preseed)
