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
        self.checksum_paths = [path.join(c.paths.iso)]

    def run(self):
        s = self.app.services
        s.pack.filesystem()
