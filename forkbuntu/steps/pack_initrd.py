from ..step import Step
from munch import munchify
from os import path

class PackInitrd(Step):
    messages = munchify({
        'past': 'packed initrd',
        'present': 'packing initrd'
    })
    requires = ['merge_initrd']

    def run(self):
        s = self.app.services
        s.initrd.pack()
