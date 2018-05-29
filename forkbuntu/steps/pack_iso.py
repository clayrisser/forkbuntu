from ..step import Step
from munch import munchify
from os import path

class PackIso(Step):
    messages = munchify({
        'past': 'packed iso',
        'present': 'packing iso',
        'cache': 'using packed iso cache'
    })
    requires = [
        'pack_filesystem'
    ]

    def __init__(self, name, app):
        super().__init__(name, app)
        c = app.conf
        self.checksum_paths = [path.join(c.paths.iso)]

    def run(self):
        s = self.app.services
        s.pack.iso()
