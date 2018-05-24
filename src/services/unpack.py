from cfoundation import Service
from os import path
import os
import shutil
import re
from subprocess import check_output, CalledProcessError, STDOUT

class Unpack(Service):
    def iso(self):
        log = self.app.log
        c = self.app.conf
        tmp_mount_path = path.join(c.paths.tmp, 'iso')
        log.debug('temporary mount path: ' + tmp_mount_path)
        if path.isdir(tmp_mount_path):
            shutil.rmtree(tmp_mount_path)
        os.makedirs(tmp_mount_path)
        if path.isdir(c.paths.mount):
            shutil.rmtree(c.paths.mount)
        self.__mount_iso(c.paths.iso, tmp_mount_path)
        shutil.copytree(tmp_mount_path, c.paths.mount, ignore=shutil.ignore_patterns('ubuntu'))
        command = 'umount ' + tmp_mount_path
        log.debug('command: ' + command)
        stdout = check_output(command, shell=True).decode('utf-8')
        log.debug(stdout)

    def __mount_iso(self, iso_path, mount_path):
        log = self.app.log
        try:
            command = 'mount -o loop ' + iso_path + ' ' + mount_path
            log.debug('command: ' + command)
            stdout = check_output(
                command,
                stderr=STDOUT,
                shell=True
            ).decode('utf-8')
            log.debug(stdout)
            return stdout
        except CalledProcessError as err:
            match = next(re.finditer(r'(\salready\smounted\son\s)(\/.*)(\.)', err.output.decode('utf-8')), None)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    mounted = match.groups()[1]
                    command = 'umount ' + mounted
                    log.debug('command: ' + command)
                    stdout = check_output(command, shell=True).decode('utf-8')
                    log.debug(stdout)
                    return self.__mount_iso(iso_path, mount_path)
            raise err

    def filesystem(self):
        log = self.app.log
        c = self.app.conf
        filesystem_parent_path = path.abspath(path.join(c.paths.filesystem, '..'))
        if path.isdir(path.join(filesystem_parent_path, 'squashfs-root')):
            shutil.rmtree(path.join(filesystem_parent_path, 'squashfs-root'))
        if path.isdir(c.paths.filesystem):
            shutil.rmtree(c.paths.filesystem)
        os.chdir(filesystem_parent_path)
        command = 'unsquashfs ' + path.join(c.paths.install, 'filesystem.squashfs')
        log.debug('command: ' + command)
        stdout = check_output(command, shell=True).decode('utf-8')
        log.debug(stdout)
        os.chdir(c.paths.cwd)
        os.rename(path.join(filesystem_parent_path, 'squashfs-root'), c.paths.filesystem)
