from ..step import Step
from munch import munchify
from os import path

class Clean(Step):
    messages = munchify({
        'past': 'cleaned',
        'present': 'cleaning'
    })
    requires = [
        'initialize'
    ]

    def run(self):
        pargs = self.app.pargs
        s = self.app.services
        s.clean.tmp()
        if pargs.cache:
            s.clean.cache()
