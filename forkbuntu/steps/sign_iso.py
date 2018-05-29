from ..step import Step
from munch import munchify
from os import path

class SignIso(Step):
    messages = munchify({
        'past': 'signed iso',
        'present': 'signing iso',
        'cache': 'using signed iso cache'
    })
    requires = [
        'configure_filesystem'
    ]

    def __init__(self, name, app):
        super().__init__(name, app)
        c = app.conf
        self.checksum_paths = [
            c.paths.apt_ftparchive,
            c.paths.indices,
            c.paths.iso,
            path.join(c.paths.cwd, 'config.yml'),
            path.join(c.paths.cwd, 'filesystem'),
            path.join(c.paths.cwd, 'iso'),
            path.join(c.paths.cwd, 'scripts'),
            path.join(c.paths.mount, 'keyring'),
            path.join(path.expanduser('~'), '.gnupg/pubring.kbx')
        ]

    def run(self):
        s = self.app.services
        s.configure.sign_iso()
