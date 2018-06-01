from ..step import Step
from munch import munchify
from os import path

class ConfigureFilesystem(Step):
    messages = munchify({
        'past': 'configured filesystem',
        'present': 'configuring filesystem'
    })
    requires = [
        'merge_filesystem'
    ]

    def run(self):
        s = self.app.services
        s.configure.filesystem()
