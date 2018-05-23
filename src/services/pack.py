from cfoundation import Service
from os import path
from pydash import _
import os

class Pack(Service):
    def iso(self):
        c = self.app.conf
        os.symlink(c.paths.mount, path.join(c.paths.mount, 'ubuntu'))
        os.system('''
        mkisofs -r -V "''' + c.name + ''' Install CD" \
        -cache-inodes \
        -J -l -b isolinux/isolinux.bin \
        -c isolinux/boot.cat -no-emul-boot \
        -boot-load-size 4 -boot-info-table \
        -o ''' + c.paths.output + ' ' + c.paths.mount
        )
        os.unlink(path.join(c.paths.mount, 'ubuntu'))

    def filesystem(self):
        c = self.app.conf
        compress = ''
        if c.filesystem.compress:
            if _.is_number(c.filesystem.compress):
                compress = ' -b ' + str(c.filesystem.compress)
            else:
                compress = ' -comp xz -e edit/boot'
        os.remove(path.join(c.paths.install, 'filesystem.squashfs'))
        os.system(
            'mksquashfs ' + c.paths.filesystem + ' ' +
            path.join(c.paths.install, 'filesystem.squashfs') + compress
        )
        size = os.popen('du -sx --block-size=1 ' + c.paths.filesystem + ' | cut -f1').read()
        with open(path.join(c.paths.install, 'filesystem.size'), 'w') as f:
            f.write(size)
