from ..step import Step
from munch import munchify
from os import path

class PackFilesystem(Step):
    messages = munchify({
        'past': 'packed filesystem',
        'present': 'packing filesystem',
        'cache': 'using packed filesystem cache'
    })
    requires = [
        'sign_iso'
    ]

    def __init__(self, name, app):
        super().__init__(name, app)
        c = app.conf
        self.checksum_paths = [
            c.paths.iso,
            path.join(c.paths.cwd, 'config.yml'),
            path.join(c.paths.cwd, 'filesystem'),
            path.join(c.paths.cwd, 'scripts'),
            path.join(c.paths.mount, 'keyring'),
            path.join(path.expanduser('~'), '.gnupg/pubring.kbx')
        ]

    def run(self):
        s = self.app.services
        s.pack.filesystem()
