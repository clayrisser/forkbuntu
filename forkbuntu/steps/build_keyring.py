from ..step import Step
from munch import munchify
from os import path

class BuildKeyring(Step):
    agnostic = True
    messages = munchify({
        'cache': 'build keyring using cache',
        'past': 'built keyring',
        'present': 'building keyring'
    })
    requires = [
        'merge_filesystem',
        'merge_iso'
    ]

    def __init__(self, name, app):
        super().__init__(name, app)
        c = app.conf
        self.checksum_paths = [
            c.paths.keyring,
            path.join(path.expanduser('~'), '.gnupg/pubring.kbx')
        ]

    def run(self):
        s = self.app.services
        s.gpg.build_keyring()
