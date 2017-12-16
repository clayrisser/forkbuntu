from __future__ import print_function
from glob import glob
from cement.core.controller import expose
from builtins import input
from os import path
from cfoundation import Controller
import os

class BuildController(Controller):
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
            }),
            (['--extras'], {
                'action': 'store',
                'dest': 'extras',
                'help': 'Extras path',
                'required': False
            }),
            (['-d', '--dist', '--distribution'], {
                'action': 'store',
                'dest': 'dist',
                'help': 'Ubuntu distribution',
                'required': False
            })
        ]

    @expose(hide=True)
    def default(self):
        s = self.app.services
        prompt = s.helper_service.prompt
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
            default_email = s.git_service.get_email()
            email = prompt('email', default_email)
        name = pargs.name
        if not name:
            default_name = s.git_service.get_name()
            name = prompt('name', default_name)
        passphrase = pargs.passphrase
        if not passphrase:
            passphrase = prompt('passphrase')
        workdir = pargs.workdir
        if not workdir:
            default_workdir = path.join(os.getcwd(), 'tmp')
            workdir = prompt('workdir', default_workdir)
        extras = pargs.extras
        if not extras:
            default_extras = path.join(os.getcwd(), 'extras')
            extras = prompt('extras', default_extras)
        dist = pargs.dist
        if not dist:
            dist = prompt('dist', 'xenial')
        self.app.log.info('image: ' + image)
        self.app.log.info('email: ' + email)
        self.app.log.info('name: ' + name)
        self.app.log.info('passphrase: ' + passphrase)
        self.app.log.info('workdir: ' + workdir)
        self.app.log.info('extras: ' + extras)
        self.app.log.info('dist: ' + dist)
        s.setup_service.validate_deps()
        s.setup_service.workdir(workdir)
        os.chdir(workdir)
        s.gpg_service.create(
            name=name,
            comment=name,
            passphrase=passphrase,
            email=email
        )
        s.image_service.mount_iso(image, workdir)
        s.image_service.clone_image_contents(workdir)
        s.image_service.unsquashfs(workdir)
        s.image_service.unmount_iso(workdir)
        s.gpg_service.generate_keyfile(
            name=name,
            comment=name,
            passphrase=passphrase,
            email=email,
            workdir=workdir
        )
        s.filesystem_service.update_filesystem_size(workdir)
        s.extras_service.copy(extras, workdir)
        s.extras_service.build_repository(workdir, name, dist)
        s.iso_service.burn(workdir)
