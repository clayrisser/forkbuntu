from __future__ import print_function
from glob import glob
from cement.core.controller import CementBaseController, expose
from builtins import input
from app.services import (
    setup_service,
    keyring_service,
    image_service,
    git_service,
    filesystem_service
)
from os import path
from app.services.helper_service import prompt
import os

class BuildController(CementBaseController):
    class Meta:
        label = 'build'
        description = 'Build Ubuntu'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['-i', '--image'], {
                'action': 'store',
                'dest': 'image',
                'help': 'Image location',
                'required': False
            }),
            (['-e', '--email'], {
                'action': 'store',
                'dest': 'email',
                'help': 'Email',
                'required': False
            }),
            (['--name'], {
                'action': 'store',
                'dest': 'name',
                'help': 'Name',
                'required': False
            }),
            (['-p', '--key-passphrase'], {
                'action': 'store',
                'dest': 'key_passphrase',
                'help': 'Key passphrase',
                'required': False
            }),
            (['-d', '--workdir'], {
                'action': 'store',
                'dest': 'basedir',
                'help': 'Base directory',
                'required': False
            })
        ]

    @expose(hide=True)
    def default(self):
        pargs = self.app.pargs
        image = pargs.image
        if not image:
            images = glob(path.join(path.expanduser('~'), 'Downloads', '*.iso'))
            default_image = None
            if len(images) > 0:
                default_image = images[0]
            image = prompt('image', default_image)
        email = pargs.email
        if not email:
            default_email = git_service.get_email()
        print('email', email)


        # image = path.abspath(path.join(os.getcwd(), pargs.image))
        # basedir = path.abspath(path.join(os.getcwd(), pargs.basedir))
        # cdsourcedir = path.abspath(path.join(basedir, 'cdsource'));
        # extrasdir = path.abspath(path.join(basedir, 'MyBuild'))
        # sourcedir = path.abspath(path.join(basedir, 'source'));
        # setup_service.validate_deps()
        # setup_service.validate_image(image)
        # setup_service.basedir(basedir, cdsourcedir, extrasdir, sourcedir)
        # os.chdir(basedir)
        # keyring_service.create(pargs.key_name, pargs.key_comment, pargs.key_passphrase, pargs.email, basedir)
        # image_service.mountiso(cdsourcedir, basedir, image)
        # image_service.clone_iso_contents(basedir, cdsourcedir)
        # image_service.unsquashfs(basedir)
        # image_service.unmountiso(cdsourcedir)
        # keyring_service.keyfile(pargs.key_name, pargs.key_comment, pargs.key_passphrase, pargs.email, basedir)
        # filesystem_service.update_filesystem_size(basedir)
