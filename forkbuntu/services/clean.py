from cfoundation import Service
from os import path
import os
import shutil

class Clean(Service):
    def tmp(self):
        c = self.app.conf
        if path.exists(c.paths.tmp):
            shutil.rmtree(c.paths.tmp)

    def cache(self, reset=False):
        c = self.app.conf
        if path.exists(c.paths.cwt):
            shutil.rmtree(c.paths.cwt)
        if path.exists(c.paths.output):
            os.remove(c.paths.output)
