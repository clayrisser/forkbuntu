from __future__ import print_function
from glob import glob
from cement.core.controller import CementBaseController, expose
from builtins import input
from app.services import (
    setup_service,
    gpg_service,
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
            (['-p', '--passphrase'], {
                'action': 'store',
                'dest': 'passphrase',
                'help': 'Passphrase',
                'required': False
            }),
            (['-w', '--workdir'], {
                'action': 'store',
                'dest': 'workdir',
                'help': 'Work directory',
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
        image = path.abspath(image)
        email = pargs.email
        if not email:
            default_email = git_service.get_email()
            email = prompt('email', default_email)
        name = pargs.name
        if not name:
            default_name = git_service.get_name()
            name = prompt('name', default_name)
        passphrase = pargs.passphrase
        if not passphrase:
            passphrase = prompt('passphrase')
        workdir = pargs.workdir
        if not workdir:
            default_workdir = path.abspath(path.join(os.getcwd(), 'tmp'))
            workdir = prompt('workdir', default_workdir)
        self.app.log.info('image: ' + image)
        self.app.log.info('email: ' + email)
        self.app.log.info('name: ' + name)
        self.app.log.info('passphrase: ' + passphrase)
        self.app.log.info('workdir: ' + workdir)
        setup_service.validate_deps(app=self.app)
        setup_service.workdir(workdir)
        os.chdir(workdir)
        gpg_service.create(
            name=name,
            comment=name,
            passphrase=passphrase,
            email=email,
            app=self.app
        )
        image_service.mountiso(image, workdir, app=self.app)
        image_service.clone_image_contents(workdir, app=self.app)
        image_service.unsquashfs(workdir, app=self.app)
        image_service.unmountiso(workdir, app=self.app)
        gpg_service.generate_keyfile(
            name=name,
            comment=name,
            passphrase=passphrase,
            email=email,
            workdir=workdir,
            app=self.app
        )
        filesystem_service.update_filesystem_size(workdir, app=self.app)
