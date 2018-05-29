from cfoundation import Service
from os import path
import shutil

class Clean(Service):
    def tmp(self):
        c = self.app.conf
        shutil.rmtree(c.paths.tmp)

    def cache(self):
        c = self.app.conf
        shutil.rmtree(path.join(c.paths.cwd, '.tmp'))
