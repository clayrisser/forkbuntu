from cfoundation import Service
from distutils.dir_util import copy_tree
from os import path
from subprocess import check_output, CalledProcessError, STDOUT
import os
import re
import shutil

class Iso(Service):
    def unpack(self):
        log = self.app.log
        c = self.app.conf
        s = self.app.services
        tmp_mount_path = path.join(c.paths.tmp, 'iso')
        log.debug('temporary mount path: ' + tmp_mount_path)
        if path.isdir(tmp_mount_path):
            shutil.rmtree(tmp_mount_path)
        os.makedirs(tmp_mount_path)
        if path.isdir(c.paths.mount):
            shutil.rmtree(c.paths.mount)
        self.__mount_iso(c.paths.iso, tmp_mount_path)
        shutil.copytree(tmp_mount_path, c.paths.mount, ignore=shutil.ignore_patterns('ubuntu'))
        s.util.subproc('umount ' + tmp_mount_path, sudo=True)

    def merge(self):
        c = self.app.conf
        s = self.app.services
        if path.isdir(path.join(c.paths.src, 'iso')):
            copy_tree(path.join(c.paths.src, 'iso'), c.paths.mount)
        s.util.stamp_template(path.join(c.paths.mount, '.disk', 'info'), description=c.description)
        s.util.stamp_template(path.join(c.paths.mount, 'README.diskdefines'), description=c.description)
        if path.isdir(path.join(c.paths.cwd, 'scripts')):
            copy_tree(path.join(c.paths.cwd, 'scripts'), path.join(c.paths.mount, 'scripts'))
        if path.isdir(path.join(c.paths.cwd, 'extras')):
            copy_tree(path.join(c.paths.cwd, 'extras'), path.join(c.paths.mount, 'pool/extras'))
        if not path.isdir(path.join(c.paths.mount, 'pool/extras')):
            os.makedirs(path.join(c.paths.mount, 'pool/extras'))
        if path.isdir(path.join(c.paths.cwd, 'iso')):
            copy_tree(path.join(c.paths.cwd, 'iso'), c.paths.mount)
        self.__write_isolinux()
        self.__write_preseed()

    def sign(self):
        c = self.app.conf
        os.system('cd ' + c.paths.mount + ''' && \
        find . -path ./isolinux -prune -o  -path ./md5sum.txt -prune -o -type f -print0 | \
        xargs -0 md5sum > md5sum.txt
        ''')

    def pack(self):
        c = self.app.conf
        log = self.app.log
        s = self.app.services
        ubuntu_symlink_path = path.join(c.paths.mount, 'ubuntu')
        if path.exists(ubuntu_symlink_path):
            os.unlink(ubuntu_symlink_path)
        os.symlink(c.paths.mount, ubuntu_symlink_path)
        s.util.subproc(
            '''mkisofs -r -V "''' + c.name + ''' Install CD" \
            -cache-inodes \
            -J -l -b isolinux/isolinux.bin \
            -c isolinux/boot.cat -no-emul-boot \
            -boot-load-size 4 -boot-info-table \
            -o ''' + c.paths.output + ' ' + c.paths.mount,
            sudo=True
        )
        os.unlink(path.join(c.paths.mount, 'ubuntu'))

    def __mount_iso(self, iso_path, mount_path):
        log = self.app.log
        s = self.app.services
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
                    s.util.subproc('umount ' + mounted, sudo=True)
                    return self.__mount_iso(iso_path, mount_path)
            raise err

    def __write_isolinux(self):
        c = self.app.conf
        s = self.app.services
        if c.preseed:
            shutil.copy(path.join(c.paths.src, 'isolinux/txt.cfg'), path.join(c.paths.mount, 'isolinux/txt.cfg'))
            s.util.stamp_template(
                path.join(c.paths.mount, 'isolinux/txt.cfg'),
                description=c.description,
                preseed=c.preseed,
                install=c.paths.install[len(c.paths.install) - 7:]
            )
            if path.exists(path.join(c.paths.cwd, 'iso/isolinux/txt.cfg')):
                lines = []
                with open(path.join(c.paths.mount, 'isolinux/txt.cfg'), 'r') as f:
                    lines = f.readlines()
                lines.append('\n')
                with open(path.join(c.paths.cwd, 'iso/isolinux/txt.cfg'), 'r') as f:
                    for line in f.readlines():
                        lines.append(line)
                with open(path.join(c.paths.mount, 'isolinux/txt.cfg'), 'w') as f:
                    f.writelines(lines)

    def __write_preseed(self):
        c = self.app.conf
        s = self.app.services
        if c.preseed:
            shutil.copy(path.join(c.paths.src, 'preseed.seed'), path.join(c.paths.mount, 'preseed', c.preseed))
            s.util.stamp_template(
                path.join(c.paths.mount, 'preseed', c.preseed),
                apt=c.apt,
                hostname=c.hostname,
                packages=c.packages
            )
            if path.exists(path.join(c.paths.cwd, 'iso/preseed', c.preseed)):
                lines = []
                with open(path.join(c.paths.mount, 'preseed', c.preseed), 'r') as f:
                    lines = f.readlines()
                lines.append('\n')
                with open(path.join(c.paths.cwd, 'iso/preseed', c.preseed), 'r') as f:
                    for line in f.readlines():
                        lines.append(line)
                with open(path.join(c.paths.mount, 'preseed', c.preseed), 'w') as f:
                    f.writelines(lines)
