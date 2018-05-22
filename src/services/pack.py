from cfoundation import Service
from os import path
import os

class Pack(Service):
    def build(self, mount_path, output_path):
        mount_path = path.abspath(mount_path)
        output_path = path.abspath(output_path)
        os.symlink(mount_path, path.join(mount_path, 'ubuntu'))
        os.system('''
        mkisofs -r -V "Custom Ubuntu Install CD" \
        -cache-inodes \
        -J -l -b isolinux/isolinux.bin \
        -c isolinux/boot.cat -no-emul-boot \
        -boot-load-size 4 -boot-info-table \
        -o ''' + output_path + ' ' + mount_path
        )
        os.unlink(path.join(mount_path, 'ubuntu'))

    def sign(self, mount_path):
        mount_path = path.abspath(mount_path)
        os.system('cd ' + mount_path + ''' && \
        find . -path ./isolinux -prune -o  -path ./md5sum.txt -prune -o -type f -print0 | \
        xargs -0 md5sum > md5sum.txt
        ''')
