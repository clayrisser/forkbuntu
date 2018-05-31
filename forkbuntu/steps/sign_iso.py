from ..step import Step
from munch import munchify
from os import path

class SignIso(Step):
    messages = munchify({
        'past': 'signed iso',
        'present': 'signing iso',
        'cache': 'using signed iso cache'
    })
    requires = [
        'create_extras',
        'pack_filesystem'
    ]

    def run(self):
        s = self.app.services
        s.configure.sign_iso()
