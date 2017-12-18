import sys
import os
import shutil
import subprocess
from app.exceptions.base_exceptions import DefaultException
from os import path
from cfoundation import Service

class SetupService(Service):

    def validate_deps(self):
        s = self.app.services
        s.task_service.started('validate_deps')
        self.verify_installed('gpg2')
        self.verify_installed('git')
        self.verify_installed('mount')
        s.task_service.finished('validate_deps')

    def init_workdir(self, workdir):
        s = self.app.services
        s.task_service.started('init_workdir')
        if not path.exists(workdir):
            os.makedirs(workdir)
        s.task_service.finished('init_workdir')

    def verify_installed(self, program):
        log = self.app.log
        pipe = subprocess.Popen(
            ['which', program],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        if pipe.stdout.readline():
            log.info('Found \'' + program + '\'')
        else:
            raise DefaultException('Failed to find \'' + program + '\'')
