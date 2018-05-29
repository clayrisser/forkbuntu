from ..step import Step
from time import sleep
from munch import munchify
from os import path

class MergeIso(Step):
    messages = munchify({
        'past': 'merged iso',
        'present': 'merging iso',
        'cache': 'using merged iso cache'
    })
    requires = [
        'unpack_iso',
        'load_config'
    ]

    def __init__(self, name, app):
        super().__init__(name, app)
        c = app.conf
        self.checksum_paths = [path.join(c.paths.iso)]

    def run(self):
        s = self.app.services
        s.configure.merge_iso()
