from ..step import Step
from munch import munchify
from os import path

class UnpackInitrd(Step):
    messages = munchify({
        'past': 'unpacked initrd',
        'present': 'unpacking initrd'
    })
    requires = ['unpack_iso']

    def run(self):
        s = self.app.services
        s.initrd.unpack()
