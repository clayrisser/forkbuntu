from app.exceptions.base_exceptions import DefaultException
from os import path
import os
import getpass

def mountiso(image, workdir, app):
    mountpath = workdir + '/cdimage'
    if not path.exists(mountpath):
        os.mkdir(mountpath)
    if os.path.isfile(mountpath + '/md5sum.txt'):
        app.log.info('Ubuntu iso already mounted')
    else:
        app.log.info('Mounting Ubuntu iso . . .')
        mounts = os.popen('mount | grep ' + mountpath).read()
        if len(mounts) > 0:
            os.popen('umount ' + mountpath).read()
        os.popen('sudo mount -o loop ' + image + ' ' + mountpath).read()
        if not os.path.isfile(mountpath + '/md5sum.txt'):
            raise DefaultException('Mounting \'' + image + '\' failed')
        else:
            app.log.info('\'' + image + '\' mounted')

def unmountiso(workdir, app):
    mountpath = workdir + '/cdimage'
    if os.path.isfile(mountpath + '/md5sum.txt'):
        os.popen('sudo umount ' + mountpath)
        os.rmdir(mountpath)
        app.log.info('Ubuntu iso unmounted')
    else:
        app.log.info('Nothing to unmount')

def unsquashfs(workdir, app):
    mountpath = workdir + '/cdimage'
    filesystempath = workdir + '/filesystem'
    if not os.path.exists(filesystempath):
        os.mkdir(filesystempath)
    os.popen('sudo unsquashfs -f -d ' + filesystempath + ' ' + mountpath + '/install/filesystem.squashfs').read()
    os.popen('sudo chown -R ' + getpass.getuser() + ':' + getpass.getuser() + ' ' + filesystempath)
    app.log.info('Filesystem unsquashed')

def clone_image_contents(workdir, app):
    mountpath = workdir + '/cdimage'
    contentspath = workdir + '/contents'
    os.popen('rsync -a --exclude ubuntu ' + mountpath + '/ ' + contentspath).read()
    os.popen('sudo chown -R ' + getpass.getuser() + ':' + getpass.getuser() + ' ' + contentspath)
    app.log.info('Image contents cloned')
