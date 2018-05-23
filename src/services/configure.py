from cfoundation import Service
from distutils.dir_util import copy_tree
from jinja2 import Template
from os import path
import os
import shutil

class Configure(Service):
    def merge_iso(self):
        c = self.app.conf
        if path.isdir(path.join(c.paths.src, 'iso')):
            copy_tree(path.join(c.paths.src, 'iso'), c.paths.mount)
        self.__stamp_template(path.join(c.paths.mount, 'preseed', 'forkbuntu.seed'), packages=c.packages)
        self.__stamp_template(path.join(c.paths.mount, '.disk', 'info'), name=c.name, version=c.version)
        self.__stamp_template(path.join(c.paths.mount, 'README.diskdefines'), name=c.name, version=c.version)
        if path.isdir(path.join(c.paths.cwd, 'scripts')):
            copy_tree(path.join(c.paths.cwd, 'scripts'), path.join(c.paths.mount, 'scripts'))
        if path.isdir(path.join(c.paths.cwd, 'iso')):
            copy_tree(path.join(c.paths.cwd, 'iso'), c.paths.mount)

    def merge_filesystem(self):
        c = self.app.conf
        if path.isdir(path.join(c.paths.src, 'filesystem')):
            copy_tree(path.join(c.paths.src, 'filesystem'), c.paths.filesystem)
        if path.isdir(path.join(c.paths.cwd, 'filesystem')):
            copy_tree(path.join(c.paths.cwd, 'filesystem'), c.paths.filesystem)

    def sign(self):
        c = self.app.conf
        os.system('cd ' + c.paths.mount + ''' && \
        find . -path ./isolinux -prune -o  -path ./md5sum.txt -prune -o -type f -print0 | \
        xargs -0 md5sum > md5sum.txt
        ''')

    def chroot(self):
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

    def __stamp_template(self, template_path, **kwargs):
        template_path = path.abspath(template_path)
        body = ''
        with open(template_path, 'r') as f:
            body = f.read()
        template = Template(body)
        body = template.render(**kwargs) + '\n'
        with open(template_path, 'w') as f:
            f.write(body)
