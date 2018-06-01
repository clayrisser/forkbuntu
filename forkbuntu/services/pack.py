from cfoundation import Service
from os import path
from pydash import _
import os

class Pack(Service):
    def iso(self):
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

    def filesystem(self):
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
