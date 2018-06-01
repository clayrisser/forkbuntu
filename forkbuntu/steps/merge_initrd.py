from ..step import Step
from munch import munchify
from os import path

class MergeInitrd(Step):
    messages = munchify({
        'past': 'merged initrd',
        'present': 'merging initrd'
    })
    requires = ['unpack_initrd']

    def run(self):
        s = self.app.services
        s.initrd.merge()
