from ..step import Step
from munch import munchify
from os import path

class Clean(Step):
    messages = munchify({
        'past': 'cleaned',
        'present': 'cleaning'
    })
    cache = False
    requires = ['initialize']

    def run(self, reset=False):
        s = self.app.services
        s.clean.tmp()
        if reset:
            s.clean.cache()
