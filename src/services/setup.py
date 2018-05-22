from cfoundation import Service
import os

class Setup(Service):
    def init(self):
        if os.geteuid() != 0:
            print('please run as root')
            exit(1)
        self.app.services.gpg.setup()
