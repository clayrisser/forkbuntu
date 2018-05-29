from ..step import Step
from time import sleep
from munch import munchify
from os import path

class UnpackIso(Step):
    messages = munchify({
        'past': 'unpacked iso',
        'present': 'unpacking iso',
        'cache': 'using iso cache'
    })
    requires = [
        'initialize'
    ]

    def __init__(self, name, app):
        super().__init__(name, app)
        c = app.conf
        self.checksum_paths = [path.join(c.paths.iso)]

    def run(self):
        s = self.app.services
        s.unpack.iso()
