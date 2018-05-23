from cfoundation import Service
import shutil

class Clean(Service):
    def tmp(self):
        c = self.app.conf
        shutil.rmtree(c.paths.tmp)
