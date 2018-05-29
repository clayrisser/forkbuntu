from ..step import Step
from munch import munchify
from os import path

class MergeFilesystem(Step):
    messages = munchify({
        'cache': 'merge filesystem using cache',
        'past': 'merged filesystem',
        'present': 'merging filesystem'
    })
    requires = [
        'unpack_filesystem',
        'merge_iso',
        'load_config'
    ]

    def __init__(self, name, app):
        super().__init__(name, app)
        c = app.conf
        self.checksum_paths = [
            c.paths.iso,
            path.join(c.paths.cwd, 'config.yml'),
            path.join(c.paths.cwd, 'filesystem'),
            path.join(c.paths.cwd, 'scripts')
        ]

    def run(self):
        s = self.app.services
        s.configure.merge_filesystem()
