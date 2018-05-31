from ..step import Step
from time import sleep
from munch import munchify
from os import path

class UnpackIso(Step):
    messages = munchify({
        'cache': 'unpack iso using cache',
        'past': 'unpacked iso',
        'present': 'unpacking iso'
    })
    requires = [
        'initialize'
    ]
    root = True

    def __init__(self, name, app):
        super().__init__(name, app)
        c = app.conf
        self.has_paths = [c.paths.output]
        self.checksum_paths = [
            c.paths.iso,
            path.join(c.paths.cwd, 'config.yml'),
            path.join(c.paths.cwd, 'filesystem'),
            path.join(c.paths.cwd, 'iso'),
            path.join(c.paths.cwd, 'scripts')
        ]

    def run(self):
        s = self.app.services
        s.unpack.iso()
