from cfoundation import Service
from os import path
from pydash import _
from subprocess import check_output, STDOUT
import os

class Pack(Service):
    def iso(self):
        log = self.app.log
        c = self.app.conf
        os.symlink(c.paths.mount, path.join(c.paths.mount, 'ubuntu'))
        command = (
            '''mkisofs -r -V "''' + c.name + ''' Install CD" \
            -cache-inodes \
            -J -l -b isolinux/isolinux.bin \
            -c isolinux/boot.cat -no-emul-boot \
            -boot-load-size 4 -boot-info-table \
            -o ''' + c.paths.output + ' ' + c.paths.mount
        )
        log.debug('command: ' + command)
        stdout = check_output(
            command,
            stderr=STDOUT,
            shell=True
        ).decode('utf-8')
        log.debug(stdout)
        os.unlink(path.join(c.paths.mount, 'ubuntu'))

    def filesystem(self):
        log = self.app.log
        c = self.app.conf
        compress = ''
        if c.filesystem.compress:
            if _.is_number(c.filesystem.compress):
                compress = ' -b ' + str(c.filesystem.compress)
            else:
                compress = ' -comp xz -e edit/boot'
        os.remove(path.join(c.paths.install, 'filesystem.squashfs'))
        command = 'mksquashfs ' + c.paths.filesystem + ' ' + path.join(c.paths.install, 'filesystem.squashfs') + compress
        log.debug('command: ' + command)
        stdout = check_output(
            command,
            shell=True
        ).decode('utf-8')
        log.debug(stdout)
        command = 'du -sx --block-size=1 ' + c.paths.filesystem + ' | cut -f1'
        log.debug('command: ' + command)
        size = check_output(command, shell=True).decode('utf-8')
        log.debug('size: ' + size)
        with open(path.join(c.paths.install, 'filesystem.size'), 'w') as f:
            f.write(size)
