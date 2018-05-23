from cfoundation import Service
from os import path
import os

class Pack(Service):
    def build(self):
        c = self.app.conf
        os.symlink(c.paths.mount, path.join(c.paths.mount, 'ubuntu'))
        os.system('''
        mkisofs -r -V "Custom Ubuntu Install CD" \
        -cache-inodes \
        -J -l -b isolinux/isolinux.bin \
        -c isolinux/boot.cat -no-emul-boot \
        -boot-load-size 4 -boot-info-table \
        -o ''' + c.paths.output + ' ' + c.paths.mount
        )
        os.unlink(path.join(c.paths.mount, 'ubuntu'))

    def sign(self):
        c = self.app.conf
        os.system('cd ' + c.paths.mount + ''' && \
        find . -path ./isolinux -prune -o  -path ./md5sum.txt -prune -o -type f -print0 | \
        xargs -0 md5sum > md5sum.txt
        ''')
