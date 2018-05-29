from ..step import Step
from time import sleep
from munch import munchify
from os import path

class MergeIso(Step):
    messages = munchify({
        'cache': 'merge iso using cache',
        'past': 'merged iso',
        'present': 'merging iso'
    })
    requires = [
        'unpack_iso',
        'load_config'
    ]

    def __init__(self, name, app):
        super().__init__(name, app)
        c = app.conf
        self.checksum_paths = [
            c.paths.iso,
            path.join(c.paths.cwd, 'config.yml'),
            path.join(c.paths.cwd, 'filesystem'),
            path.join(c.paths.cwd, 'iso'),
            path.join(c.paths.cwd, 'scripts')
        ]

    def run(self):
        s = self.app.services
        s.configure.merge_iso()
