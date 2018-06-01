from ..step import Step
from munch import munchify
from os import path

class MergeIso(Step):
    messages = munchify({
        'past': 'merged iso',
        'present': 'merging iso'
    })
    requires = ['load_config']

    def run(self):
        s = self.app.services
        s.iso.merge()
