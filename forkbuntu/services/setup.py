from cfoundation import Service
from halo import Halo
import os

class Setup(Service):
    def init(self):
        s = self.app.services
        if os.geteuid() != 0:
            self.app.spinner.fail('please run as root')
            exit(1)
        s.gpg.restart()
