from app.exceptions.base_exceptions import DefaultException
from os import path
import os
import getpass
from cfoundation import Service

class ImageService(Service):

    def mount_iso(self, image, workdir):
        log = self.app.log
        s = self.app.services
        s.task_service.started('mount_iso')
        image_path = workdir + '/image'
        if not path.exists(image_path):
            os.mkdir(image_path)
        if os.path.isfile(image_path + '/md5sum.txt'):
            log.info('Ubuntu iso already mounted')
        else:
            mounts = os.popen('mount | grep ' + image_path).read()
            if len(mounts) > 0:
                os.popen('umount ' + image_path).read()
            os.popen('mount -o loop ' + image + ' ' + image_path).read()
            if not os.path.isfile(image_path + '/md5sum.txt'):
                raise DefaultException('Mounting \'' + image + '\' failed')
        s.task_service.finished('mount_iso')

    def unmount_iso(self, workdir):
        log = self.app.log
        s = self.app.services
        s.task_service.started('unmount_iso')
        image_path = workdir + '/image'
        if os.path.isfile(image_path + '/md5sum.txt'):
            os.popen('umount ' + image_path)
            os.rmdir(image_path)
        else:
            log.info('Nothing to unmount')
        s.task_service.finished('unmount_iso')

    def unsquashfs(self, workdir):
        s = self.app.services
        s.task_service.started('unsquashfs')
        image_path = workdir + '/image'
        filesystem_path = workdir + '/filesystem'
        if not os.path.exists(filesystem_path):
            os.mkdir(filesystem_path)
        os.popen('unsquashfs -f -d ' + filesystem_path + ' ' + image_path + '/install/filesystem.squashfs').read()
        s.task_service.finished('unsquashfs')

    def clone_image_contents(self, workdir):
        s = self.app.services
        s.task_service.started('clone_image_contents')
        image_path = workdir + '/image'
        contentspath = workdir + '/contents'
        os.popen('rsync -a --exclude ubuntu ' + image_path + '/ ' + contentspath).read()
        s.task_service.finished('clone_image_contents')

    def burn(self, workdir, output_path):
        s = self.app.services
        s.task_service.started('burn_image')
        contents_path = path.join(workdir, 'contents')
        os.chdir(contents_path)
        os.system('''
        xorriso -as mkisofs -r -V "Custom Ubuntu Install CD" \
        -cache-inodes \
        -J -l -b isolinux/isolinux.bin \
        -c isolinux/boot.cat -no-emul-boot \
        -boot-load-size 4 -boot-info-table \
        -o ''' + output_path + ' ' + contents_path + '''
        ''')
        os.chdir(workdir)
        s.task_service.finished('burn_image')
