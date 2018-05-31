from ..step import Step
from munch import munchify
from os import path

class ConfigureFilesystem(Step):
    messages = munchify({
        'cache': 'configure filesystem using cache',
        'past': 'configured filesystem',
        'present': 'configuring filesystem'
    })
    requires = [
        'merge_filesystem'
    ]

    def run(self):
        s = self.app.services
        s.configure.filesystem()
