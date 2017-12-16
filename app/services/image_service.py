from app.exceptions.base_exceptions import DefaultException
from os import path
import os
import getpass
from cfoundation import Service

class ImageService(Service):

    def mount_iso(self, image, workdir):
        log = self.app.log
        log.info('^ started image mount iso')
        image_path = workdir + '/image'
        if not path.exists(image_path):
            os.mkdir(image_path)
        if os.path.isfile(image_path + '/md5sum.txt'):
            log.info('ubuntu iso already mounted')
        else:
            mounts = os.popen('mount | grep ' + image_path).read()
            if len(mounts) > 0:
                os.popen('umount ' + image_path).read()
            os.popen('sudo mount -o loop ' + image + ' ' + image_path).read()
            if not os.path.isfile(image_path + '/md5sum.txt'):
                raise DefaultException('Mounting \'' + image + '\' failed')
        log.info('$ finished image mount iso')

    def unmount_iso(self, workdir):
        log = self.app.log
        log.info('^ started unmount iso')
        image_path = workdir + '/image'
        if os.path.isfile(image_path + '/md5sum.txt'):
            os.popen('sudo umount ' + image_path)
            os.rmdir(image_path)
        else:
            log.info('nothing to unmount')
        log.info('$ finished unmount iso')

    def unsquashfs(self, workdir):
        log = self.app.log
        log.info('^ started unsquashfs')
        image_path = workdir + '/image'
        filesystem_path = workdir + '/filesystem'
        if not os.path.exists(filesystem_path):
            os.mkdir(filesystem_path)
        os.popen('sudo unsquashfs -f -d ' + filesystem_path + ' ' + image_path + '/install/filesystem.squashfs').read()
        os.popen('sudo chown -R ' + getpass.getuser() + ':' + getpass.getuser() + ' ' + filesystem_path)
        log.info('$ finished unsquashfs')

    def clone_image_contents(self, workdir):
        log = self.app.log
        log.info('^ started clone image contents')
        image_path = workdir + '/image'
        contentspath = workdir + '/contents'
        os.popen('rsync -a --exclude ubuntu ' + image_path + '/ ' + contentspath).read()
        os.popen('sudo chown -R ' + getpass.getuser() + ':' + getpass.getuser() + ' ' + contentspath)
        log.info('$ finished clone image contents')
