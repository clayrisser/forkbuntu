from cfoundation import Service
from os import path
import os
from distutils.dir_util import copy_tree

class Configure(Service):
    def merge(self, mount_path):
        mount_path = path.abspath(mount_path)
        copy_tree(path.join(os.getcwd(), 'iso'), mount_path)

    def preseed(self, mount_path):
        mount_path = path.abspath(mount_path)
