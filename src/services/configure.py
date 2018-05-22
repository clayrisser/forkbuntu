from cfoundation import Service
from os import path
import os
from distutils.dir_util import copy_tree

class Configure(Service):
    def merge_files(self, working_path, mount_path):
        src_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), '..'))
        working_path = path.abspath(working_path)
        mount_path = path.abspath(mount_path)
        copy_tree(path.join(src_path, 'iso'), mount_path)
        if path.isdir(path.join(working_path, 'scripts')):
            copy_tree(path.join(working_path, 'scripts'), path.join(mount_path, 'scripts'))
        if path.isdir(path.join(working_path, 'iso')):
            copy_tree(path.join(working_path, 'iso'), mount_path)

    def preseed(self, mount_path):
        mount_path = path.abspath(mount_path)
