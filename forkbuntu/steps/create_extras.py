from ..step import Step
from munch import munchify
from os import path

class CreateExtras(Step):
    agnostic = True
    messages = munchify({
        'past': 'created extras',
        'present': 'creating extras',
    })
    requires = ['build_keyring']

    def init(self):
        c = self.app.conf
        self.checksum_paths = [
            c.paths.apt_ftparchive,
            c.paths.indices
        ]

    def run(self):
        s = self.app.services
        s.extras.create()
