from cfoundation import Service
from os import path
import os

class Setup(Service):
    def init(self):
        c = self.app.conf
        s = self.app.services
        if os.geteuid() != 0:
            self.app.spinner.fail('please run as root')
            exit(1)
        if not path.isdir(c.paths.cwt):
            os.makedirs(c.paths.cwt)
