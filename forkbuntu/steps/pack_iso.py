from ..step import Step
from munch import munchify
from os import path

class PackIso(Step):
    messages = munchify({
        'past': 'packed iso',
        'present': 'packing iso'
    })
    requires = ['sign_iso']

    def run(self):
        s = self.app.services
        s.iso.pack()
