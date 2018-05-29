from ..step import Step
from munch import munchify
from os import path

class CreateExtras(Step):
    messages = munchify({
        'past': 'created extras',
        'present': 'creating extras',
        'cache': 'using extras cache'
    })
    requires = [
        'build_keyring'
    ]

    def __init__(self, name, app):
        super().__init__(name, app)
        c = app.conf
        self.checksum_paths = [path.join(c.paths.iso)]

    def run(self):
        s = self.app.services
        s.extras.create()
