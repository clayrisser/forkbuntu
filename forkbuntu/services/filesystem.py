from cfoundation import Service
from distutils.dir_util import copy_tree
from os import path
from pydash import _
import os
import shutil

class Filesystem(Service):
    def unpack(self):
        log = self.app.log
        c = self.app.conf
        s = self.app.services
        filesystem_parent_path = path.abspath(path.join(c.paths.filesystem, '..'))
        if path.isdir(path.join(filesystem_parent_path, 'squashfs-root')):
            shutil.rmtree(path.join(filesystem_parent_path, 'squashfs-root'))
        if path.isdir(c.paths.filesystem):
            shutil.rmtree(c.paths.filesystem)
        os.chdir(filesystem_parent_path)
        s.util.subproc('unsquashfs ' + path.join(c.paths.install, 'filesystem.squashfs'), sudo=True)
        os.chdir(c.paths.cwd)
        os.rename(path.join(filesystem_parent_path, 'squashfs-root'), c.paths.filesystem)

    def merge(self):
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


    def configure(self):
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

    def pack(self):
        c = self.app.conf
        compress = ''
        log = self.app.log
        s = self.app.services
        if c.filesystem.compress:
            if _.is_number(c.filesystem.compress):
                compress = ' -b ' + str(c.filesystem.compress)
            else:
                compress = ' -comp xz -e edit/boot'
        os.remove(path.join(c.paths.install, 'filesystem.squashfs'))
        s.util.subproc(
            'mksquashfs ' + c.paths.filesystem + ' '
            + path.join(c.paths.install, 'filesystem.squashfs') + compress,
            sudo=True
        )
        size = s.util.subproc('du -sx --block-size=1 ' + c.paths.filesystem + ' | cut -f1', sudo=True)
        log.debug('size: ' + size)
        with open(path.join(c.paths.install, 'filesystem.size'), 'w') as f:
            f.write(size)
