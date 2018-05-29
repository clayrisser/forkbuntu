from ..step import Step
from munch import munchify
from os import path

class ConfigureFilesystem(Step):
    messages = munchify({
        'cache': 'configure filesystem using cache',
        'past': 'configured filesystem',
        'present': 'configuring filesystem'
    })
    requires = [
        'create_extras'
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
        s.configure.filesystem()
