from ..step import Step
from time import sleep
from munch import munchify
from os import path

class UnpackFilesystem(Step):
    messages = munchify({
        'cache': 'unpack filesystem using cache',
        'past': 'unpacked filesystem',
        'present': 'unpacking filesystem'
    })
    requires = [
        'unpack_iso'
    ]

    def run(self):
        s = self.app.services
        s.unpack.filesystem()
