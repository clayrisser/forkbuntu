from ..step import Step
from munch import munchify
from os import path

class MergeFilesystem(Step):
    messages = munchify({
        'cache': 'merge filesystem using cache',
        'past': 'merged filesystem',
        'present': 'merging filesystem'
    })
    requires = [
        'load_config'
    ]

    def run(self):
        s = self.app.services
        s.configure.merge_filesystem()
