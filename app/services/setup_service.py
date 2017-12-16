import sys
import os
from app.exceptions.base_exceptions import DefaultException
from os import path
from cfoundation import Service

class SetupService(Service):

    def validate_deps(self):
        log = self.app.log
        log.info('^ started setup validate deps')
        if self.is_installed('gpg2'):
            log.info('found gpg2')
        else:
            raise DefaultException('gpg required to generate signing keys')
        log.info('$ finished setup validate deps')

    def workdir(self, workdir):
        if not path.exists(workdir):
            os.mkdir(workdir)

    def mkdir(self, path):
        try:
            os.makedirs(path)
        except OSError:
            pass

    def is_installed(self, program):
        res = os.system('which ' + program + ' > /dev/null')
        if res == 0:
            return True
        else:
            return False
