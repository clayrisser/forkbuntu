from ..step import Step
from munch import munchify
from os import path

class BuildKeyring(Step):
    messages = munchify({
        'past': 'built keyring',
        'present': 'building keyring',
        'cache': 'using built keyring cache'
    })
    requires = [
        'merge_filesystem'
    ]

    def __init__(self, name, app):
        super().__init__(name, app)
        c = app.conf
        self.checksum_paths = [path.join(c.paths.iso)]

    def run(self):
        s = self.app.services
        s.gpg.build_keyring()
