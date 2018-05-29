from ..step import Step
from munch import munchify
from os import path

class Clean(Step):
    messages = munchify({
        'past': 'cleaned',
        'present': 'cleaning'
    })
    requires = [
        'pack_iso'
    ]

    def run(self):
        s = self.app.services
        s.clean.tmp()
