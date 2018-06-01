from ..step import Step
from munch import munchify
from os import path

class SignIso(Step):
    messages = munchify({
        'past': 'signed iso',
        'present': 'signing iso'
    })
    requires = [
        'create_extras',
        'pack_filesystem'
    ]

    def __init__(self, name, app):
        super().__init__(name, app)
        c = app.conf
        if path.exists(path.join(c.paths.cwd, 'initrd')):
            self.requires.append('pack_initrd')

    def run(self):
        s = self.app.services
        s.iso.sign()
