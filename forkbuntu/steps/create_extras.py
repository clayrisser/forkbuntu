from ..step import Step
from munch import munchify
from os import path

class CreateExtras(Step):
    messages = munchify({
        'cache': 'create extras using cache',
        'past': 'created extras',
        'present': 'creating extras',
    })
    requires = [
        'build_keyring'
    ]

    def __init__(self, name, app):
        super().__init__(name, app)
        c = app.conf
        self.checksum_paths = [
            c.paths.apt_ftparchive,
            c.paths.indices,
            c.paths.iso,
            path.join(c.paths.cwd, 'config.yml'),
            path.join(c.paths.cwd, 'iso')
        ]

    def run(self):
        s = self.app.services
        s.extras.create()
