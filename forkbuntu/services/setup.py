from cfoundation import Service
from os import path
from pydash import _
import os
import shutil
import sys

class Setup(Service):
    missing_programs = []

    def init(self):
        spinner = self.app.spinner
        if os.geteuid() != 0:
            self.app.spinner.fail('please run as root')
            exit(1)
        self.__has_program('apt-ftparchive')
        self.__has_program('apt-ftparchive')
        self.__has_program('apt-get')
        self.__has_program('bash')
        self.__has_program('cat')
        self.__has_program('chmod')
        self.__has_program('chown')
        self.__has_program('chown')
        self.__has_program('curl')
        self.__has_program('cut')
        self.__has_program('dpkg-buildpackage')
        self.__has_program('du')
        self.__has_program('fakeroot')
        self.__has_program('find')
        self.__has_program('gpg')
        self.__has_program('gzip')
        self.__has_program('mkisofs')
        self.__has_program('mksquashfs')
        self.__has_program('mount')
        self.__has_program('rngd')
        self.__has_program('sudo')
        self.__has_program('umount')
        self.__has_program('unsquashfs')
        if len(self.missing_programs) > 0:
            spinner.fail('missing the following programs')
            sys.stdout.writelines(_.map(self.missing_programs, lambda x: x + '\n'))
            exit(1)

    def __has_program(self, program):
        program_path = shutil.which(program)
        if not program_path or len(program_path) <= 0:
            self.missing_programs.append(program)
            return False
        return True
