from ..step import Step
from time import sleep
from munch import munchify
from os import path

class UnpackFilesystem(Step):
    messages = munchify({
        'past': 'unpacked filesystem',
        'present': 'unpacking filesystem',
        'cache': 'using filesystem cache'
    })
    requires = [
        'unpack_iso'
    ]

    def __init__(self, name, app):
        super().__init__(name, app)
        c = app.conf
        self.checksum_paths = [
            path.join(c.paths.cwd, 'config.yml'),
            path.join(c.paths.cwd, 'filesystem'),
            path.join(c.paths.cwd, 'iso'),
            path.join(path.join(c.paths.mount, 'install/filesystem.squashfs'))
        ]

    def run(self):
        s = self.app.services
        s.unpack.filesystem()
