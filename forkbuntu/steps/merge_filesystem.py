from ..step import Step
from munch import munchify
from os import path

class MergeFilesystem(Step):
    messages = munchify({
        'past': 'merged filesystem',
        'present': 'merging filesystem',
        'cache': 'using merged filesystem cache'
    })
    requires = [
        'unpack_filesystem',
        'merge_iso',
        'load_config'
    ]

    def __init__(self, name, app):
        super().__init__(name, app)
        c = app.conf
        self.checksum_paths = [path.join(c.paths.iso)]

    def run(self):
        s = self.app.services
        s.configure.merge_filesystem()
