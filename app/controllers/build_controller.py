from __future__ import print_function
import getpass
import os
from app.exceptions.base_exceptions import DefaultException
from builtins import input
from cement.core.controller import expose
from cfoundation import Controller
from glob import glob
from os import path

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
                'help': 'GPG passphrase',
                'required': False
            }),
            (['-w', '--workdir'], {
                'action': 'store',
                'dest': 'workdir',
                'help': 'Working directory',
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
            }),
            (['-o', '--output'], {
                'action': 'store',
                'dest': 'output',
                'help': 'Image output path',
                'required': False
            })
        ]

    @expose(hide=True)
    def default(self):
        s = self.app.services
        prompt = s.helper_service.prompt
        pargs = self.app.pargs
        os.system('sudo echo')
        s.setup_service.validate_deps()
        image = pargs.image
        if not image:
            default_image = s.helper_service.find_image()
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
            passphrase = prompt('gpg passphrase', private=True)
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
        output = pargs.output
        if not output:
            default_output = path.join(os.getcwd(), 'custom.iso')
            output = path.abspath(path.join(os.getcwd(), prompt('output', default_output)))
        s.setup_service.init_workdir(workdir)
        os.chdir(workdir)
        s.gpg_service.create_key(
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
        s.extras_service.build_repository(
            workdir,
            name=name,
            passphrase=passphrase,
            dist=dist
        )
        s.image_service.burn(workdir, output)
