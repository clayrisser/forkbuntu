from app.exceptions.base_exceptions import DefaultException
import os

def mountiso(cdsourcedir, basedir, image):
    if os.path.isfile(cdsourcedir + '/md5sum.txt'):
        print('Ubuntu iso already mounted')
    else:
        print('Mounting Ubuntu iso . . .')
        response = os.system('mount | grep ' + cdsourcedir)
        if response == 0:
            os.system('umount ' + cdsourcedir)
        os.system('mount -o loop ' + image + ' ' + cdsourcedir)
        if not os.path.isfile(cdsourcedir + '/md5sum.txt'):
            raise DefaultException('Mount did not succeed')
        else:
            print('Mount successful')

def unmountiso(cdsourcedir):
    if os.path.isfile(cdsourcedir + '/md5sum.txt'):
        os.system('umount ' + cdsourcedir)
        print('Ubuntu iso unmounted')
    else:
        print('Nothing to unmount')

def unsquashfs(basedir):
    print('Unsquashing . . .')
    if not os.path.exists(basedir + '/filesystem'):
        os.mkdir(basedir + '/filesystem')
    os.system('unsquashfs -f -d ' + basedir + '/filesystem ' + basedir + '/FinalCD/install/filesystem.squashfs')

def squashfs():
    pass

def clone_iso_contents(basedir, cdsourcedir):
    print('Re-syncing old data . . .')
    os.system('rsync -a --exclude ubuntu ' + cdsourcedir + '/ ' + basedir + '/FinalCD/')
