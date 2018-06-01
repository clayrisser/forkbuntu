from cfoundation import Service
from distutils.dir_util import copy_tree
from munch import Munch
from os import path
import os
import re
import shutil

class Configure(Service):
    def merge_iso(self):
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

    def load_release(self):
        c = self.app.conf
        release = Munch()
        matches = None
        with open(path.join(c.paths.filesystem, 'etc/lsb-release'), 'r') as f:
            matches = re.finditer(r'(^[^=\n\s]+)\=([^\=\n]*$)', f.read(), re.MULTILINE)
        for key, match in enumerate(matches):
            groups = match.groups()
            if (len(groups) >= 2):
                value = groups[1]
                if (value.startswith('"') and value.endswith('"')) or (value.startswith('\'') and value.endswith('\'')):
                    value = value[1:-1]
                release[groups[0].lower()] = value
        return release

    def merge_filesystem(self):
        c = self.app.conf
        s = self.app.services
        if path.isdir(path.join(c.paths.src, 'filesystem')):
            copy_tree(path.join(c.paths.src, 'filesystem'), c.paths.filesystem)
        s.util.stamp_template(
            path.join(c.paths.filesystem, 'etc/lsb-release'),
            codename=c.codename,
            description=c.description,
            distrib_id=c.distrib_id,
            version=c.version
        )
        if path.isdir(path.join(c.paths.cwd, 'filesystem')):
            copy_tree(path.join(c.paths.cwd, 'filesystem'), c.paths.filesystem)

    def sign_iso(self):
        c = self.app.conf
        os.system('cd ' + c.paths.mount + ''' && \
        find . -path ./isolinux -prune -o  -path ./md5sum.txt -prune -o -type f -print0 | \
        xargs -0 md5sum > md5sum.txt
        ''')

    def filesystem(self):
        c = self.app.conf
        os.rename(path.join(c.paths.filesystem, 'etc/resolv.conf'), path.join(c.paths.filesystem, 'etc/_resolv.conf'))
        shutil.copyfile(path.abspath('/etc/resolv.conf'), path.join(c.paths.filesystem, 'etc/resolv.conf'))
        copy_tree(path.join(c.paths.mount, 'scripts'), path.join(c.paths.filesystem, 'root/scripts'))
        os.system('mount --bind ' + path.abspath('/dev') + ' ' + path.join(c.paths.filesystem, 'dev'))
        root = os.open('/', os.O_RDONLY)
        os.chroot(c.paths.filesystem)
        os.chdir('/')
        os.system('mount -t proc none /proc')
        os.system('mount -t sysfs none /sys')
        os.system('mount -t devpts none /dev/pts')
        os.environ['HOME'] = path.abspath('/root')
        os.environ['LC_ALL'] = 'C'
        os.system('bash /root/scripts/filesystem.sh')
        os.system('umount /proc || umount -lf /proc')
        os.system('umount /sys')
        os.system('umount /dev/pts')
        os.fchdir(root)
        os.chroot('.')
        os.close(root)
        os.system('umount ' + path.join(c.paths.filesystem, 'dev'))
        shutil.rmtree(path.join(c.paths.filesystem, 'root/scripts'))
        os.rename(path.join(c.paths.filesystem, 'etc/_resolv.conf'), path.join(c.paths.filesystem, 'etc/resolv.conf'))

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
